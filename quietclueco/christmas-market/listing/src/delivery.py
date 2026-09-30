"""Build the Etsy delivery folder: the three case books plus one ZIP with the three solution files."""
import os, shutil, zipfile
import case_listing as CL

ETSY_LIMIT_MB = 20

def build(outdir):
    if os.path.isdir(outdir):
        shutil.rmtree(outdir)
    os.makedirs(outdir)
    files = []
    for key in ("letter", "a4", "ipad"):
        dst = os.path.join(outdir, os.path.basename(CL.PDF[key]))
        shutil.copyfile(CL.PDF[key], dst); files.append(dst)
    z = os.path.join(outdir, f"{CL.SLUG}_SOLUTION.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for key in ("letter", "a4", "ipad"):
            zf.write(CL.SOLUTION[key], arcname=os.path.basename(CL.SOLUTION[key]))
    files.append(z)
    report = []
    for f in files:
        mb = os.path.getsize(f) / 1024 / 1024
        report.append(dict(file=os.path.basename(f), mb=round(mb, 2), ok=mb < ETSY_LIMIT_MB))
    with zipfile.ZipFile(z) as zf:
        inside = zf.namelist()
        bad = zf.testzip()
    return report, inside, bad
