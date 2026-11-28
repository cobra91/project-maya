"""lab/ik2_release_vs_lab.py - the release's maya-ik2 against this branch's, on one PC: the same model, the same prompt,
the races interleaved, the generated tokens compared.

    python lab/ik2_release_vs_lab.py --release EXE --lab EXE [--only SUBSTRING] [--races 2] [--stop-task "\\llama-swap"]

The arms: the release as it ships, the release with a setting it already has (`IK2_PEER_DIRECT_SIGNAL=1`), this branch
as it is, and this branch with what it adds (`IK2_RESIDENT_UNFUSED=1`, a DFlash2 drafter). A run: the engine on the
command line, greedy, FP8 cache, the expert profile, 512 tokens over lab/ids302.txt (302 tokens). --stop-task ends a
scheduled task for the races and runs it again after (a router that holds the cards otherwise).

The models and the drafter are where this PC keeps them (MODELS below): change them for yours.
"""
import argparse
import json
import os
import re
import statistics
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = {
    "q4": "D:/StrataModels/models/Inkling-2-Mini-UD-Q4_K_XL.gguf",   # unsloth's file of before 2026-11-23
    "iq3": "D:/test/models/Inkling-2-Mini-UD-IQ3_XXS-old.gguf",     # its Old_Support copy
    "iq3_new": "D:/test/models/Inkling-2-Mini-UD-IQ3_XXS.gguf",     # the repo's file since 2026-11-23
}
DSPARK = "D:/test/models/dspark-Inkling-2-Mini-Q8_0.gguf"
DFLASH2 = "D:/test/models/Inkling-2-Mini-DFlash2-Q8_0.gguf"
PROFILE = "D:/test/maya-link/data/expert-profile-ik2mini.bin"
HEALTH = "http://127.0.0.1:11434/health"


def arm(name, exe, env=None, model=None, dflash2=False):
    """An arm: its name, the engine, its settings, and where it differs from its case (the model, the drafter)."""
    return {"name": name, "exe": exe, "env": env or {}, "model": model, "dflash2": dflash2}


CASES = {}


def case(cid, cards, model, ctx, drafting, arms):
    CASES[cid] = {"cards": cards, "model": model, "ctx": ctx, "drafting": drafting, "arms": arms}


def vram():
    try:
        o = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"], capture_output=True,
                           text=True, timeout=15).stdout
        return sum(int(x) for x in o.split())
    except Exception:
        return 0


def health():
    try:
        return urllib.request.urlopen(HEALTH, timeout=2).status
    except Exception:
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", required=True)
    ap.add_argument("--lab", required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--races", type=int, default=2)
    ap.add_argument("--gen", type=int, default=512)
    ap.add_argument("--stop-task", default="")
    ap.add_argument("--out", default=os.path.join(HERE, "results", "last.json"))
    a = ap.parse_args()
    R, L = a.release, a.lab
    ring = {"IK2_PEER_DIRECT_SIGNAL": "1"}
    resident = {"IK2_RESIDENT_UNFUSED": "1"}
    rel, lab = arm("release", R), arm("lab", L)
    rel_ring, lab_ring = arm("release+ring", R, ring), arm("lab+ring", L, ring)
    lab_res = arm("lab+resident", L, resident)
    lab_res_new = arm("lab+resident, new file", L, resident, model="iq3_new")

    def df2(name, env, w, model=None):
        return arm(name, L, dict(env, IK2_DRAFT_WIDTH=str(w)), model=model, dflash2=True)

    case("q4_5080", "0", "q4", 32768, None, [rel, lab])
    case("q4_ti", "1", "q4", 32768, None, [rel, lab])
    case("q4_dual", "", "q4", 32768, None, [rel, rel_ring, lab, lab_ring])
    case("q4_5080_dspark", "0", "q4", 32768, "dspark", [rel, lab])
    case("q4_ti_dspark", "1", "q4", 32768, "dspark", [rel, lab])
    case("q4_dual_dspark", "", "q4", 32768, "dspark", [rel, rel_ring, lab, lab_ring])
    case("q4_dual_dflash2", "", "q4", 32768, None,
         [lab_ring, df2("lab+ring+DFlash2 w6", ring, 6), df2("lab+ring+DFlash2 w4", ring, 4)])
    case("iq3_5080", "0", "iq3", 32768, None, [rel, lab, lab_res, lab_res_new])
    case("iq3_ti", "1", "iq3", 32768, None, [rel, lab, lab_res, lab_res_new])
    case("iq3_5080_dspark", "0", "iq3", 16384, "dspark", [rel, lab_res])
    case("iq3_ti_dspark", "1", "iq3", 16384, "dspark", [rel, lab_res])
    case("iq3_dual_dspark", "", "iq3", 16384, "dspark", [rel, lab_res])
    case("iq3_5080_dflash2", "0", "iq3_new", 16384, "dspark",
         [lab_res_new, df2("lab+resident+DFlash2 w4", resident, 4), df2("lab+resident+DFlash2 w6", resident, 6)])

    ids_arg = "@" + os.path.join(HERE, "ids302.txt").replace("\\", "/")
    outdir = os.path.join(HERE, "results")
    results = {}

    def wanted(cid):   # (--only: comma-separated - a case's id, or a part of one)
        return not a.only or any(p == cid or (p not in CASES and p in cid) for p in a.only.split(","))

    def task(run):
        if not a.stop_task:
            return
        subprocess.run(["schtasks", "/Run" if run else "/End", "/TN", a.stop_task], capture_output=True)
        if run:
            for _ in range(40):
                time.sleep(2)
                if health() == 200:
                    break
        else:
            time.sleep(2)

    def run_one(cid, ar, race):
        c = CASES[cid]
        env = dict(os.environ, IK2_KV="fp8", IK2_WARM=PROFILE)
        env.pop("CUDA_VISIBLE_DEVICES", None)
        if c["cards"]:
            env["CUDA_VISIBLE_DEVICES"] = c["cards"]
        env.update(ar["env"])
        model = MODELS[ar["model"] or c["model"]]
        cmd = [ar["exe"], "--model", model, "--gpus", "2" if c["cards"] == "" else "1", "--tokens", ids_arg, "--gen", str(a.gen),
               "--eos", "-1", "--max-context", str(c["ctx"])]
        if c["drafting"] == "dspark":
            cmd += ["--draft", DSPARK, "--drafting", "on"]
        if c["drafting"] == "dflash2" or ar["dflash2"]:
            cmd += ["--draft", DFLASH2, "--drafting", "on"]
        os.makedirs(outdir, exist_ok=True)
        log = os.path.join(outdir, "%s__%s__%d.log" % (cid, re.sub(r"[^A-Za-z0-9]+", "-", ar["name"]), race))
        t0 = time.time()
        with open(log, "wb") as f:
            try:
                p = subprocess.run(cmd, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=300)
                rc = "code %d" % p.returncode
            except subprocess.TimeoutExpired:
                rc = "STOPPED (killed at 300 s)"
        out = open(log, encoding="utf-8", errors="replace").read().splitlines()
        r = {"rc": rc, "s": time.time() - t0, "model": os.path.basename(model), "log": os.path.basename(log)}
        for l in out:
            if l.startswith("generated: ") and "tokens" not in r:
                r["tokens"] = [int(x) for x in l[11:].replace(",", " ").split()]
            elif l.startswith("generation: "):
                m = re.search(r"\(([\d.]+) tok/s\)", l)
                if m:
                    r["tok_s"] = float(m.group(1))
                r["generation"] = l[:90]
            elif ("resident path" in l or l.startswith("resident:") or " experts in VRAM" in l or l.startswith("two GPUs:")
                  or "hand-offs between GPUs" in l or l.startswith("NOTE") or "could not be pinned" in l or "no key" in l
                  or "measured:" in l or "not read" in l):
                r.setdefault("notes", []).append(l[:140])
        results.setdefault(cid, {}).setdefault(ar["name"], []).append(r)
        return r

    if vram() > 300:
        print("ABORT: %d MiB already on the cards" % vram())
        sys.exit(3)
    task(False)
    try:
        for cid in CASES:
            if not wanted(cid):
                continue
            for race in range(a.races):
                for ar in CASES[cid]["arms"]:
                    if vram() > 300:
                        print("ABORT %s: another process on the cards" % cid)
                        raise SystemExit(3)
                    r = run_one(cid, ar, race)
                    print("%-18s %-27s race %d: %-26s %s" % (
                        cid, ar["name"], race + 1, r.get("generation", r["rc"]).split(";")[0][:60],
                        ("%.1f tok/s" % r["tok_s"]) if "tok_s" in r else ""), flush=True)
    finally:
        left = subprocess.run(["nvidia-smi", "--query-compute-apps=pid,process_name", "--format=csv,noheader"], capture_output=True,
                              text=True).stdout.strip()
        if left:
            print("!!! PROCESSES STILL HOLD THE CARDS:\n" + left)
        task(True)
        os.makedirs(outdir, exist_ok=True)
        json.dump(results, open(a.out, "w"), indent=1)
    print()
    for cid, arms in results.items():
        c = CASES[cid]
        print("== %s: %s, ctx %d, %s" % (cid, {"0": "RTX 5080", "1": "RTX 4060 Ti", "": "two cards"}[c["cards"]], c["ctx"],
                                         c["drafting"] or "no drafting"))
        first = next((v[0].get("tokens") for v in arms.values() if v and v[0].get("tokens")), None)
        for n, v in arms.items():
            t = [x["tok_s"] for x in v if "tok_s" in x]
            tok = v[0].get("tokens")
            same = "-" if not tok else ("same tokens" if first is not None and tok == first else "other tokens")
            note = next((l for x in v for l in x.get("notes", []) if "resident" in l or "hand-offs" in l), "")
            print("   %-27s %-30s %-13s %s" % (
                n, ("%.1f tok/s (%s)" % (statistics.median(t), " / ".join("%.1f" % x for x in t))) if t else v[0]["rc"], same, note[:120]))


if __name__ == "__main__":
    main()
