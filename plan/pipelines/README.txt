Canonical pipeline documentation and BIDS examples for Gugger Lab Infra live here:

  /mnt/nfs/Gugger_Lab/Infra/pipelines

Edit files there (or sync from here after local edits). Canonical build scripts live under Training USER_GUIDE:

  /mnt/nfs/Gugger_Lab/Infra/Training/USER_GUIDE/Scripts/

Regenerate combined pipelines doc (wrapper also works at Infra/pipelines):

  python3 /mnt/nfs/Gugger_Lab/Infra/Training/USER_GUIDE/Scripts/build_pipelines_docx.py

Per-modality BIDS documentation (Training library) lives here:

  /mnt/nfs/Gugger_Lab/Infra/Training/Pipelines/BIDS

See BIDS/README.docx for the index. Content is BIDS-only; regenerate with python3 build_bids_training_docx.py. README.txt in that folder explains the layout.

HippUnfold-only pipeline documentation (Word):

  /mnt/nfs/Gugger_Lab/Infra/Training/Pipelines/hippunfold/HippUnfold_pipeline_documentation.docx
