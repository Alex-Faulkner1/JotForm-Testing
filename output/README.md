# Output Directory

This directory stores test run outputs organized by EFS reference.

## Structure

Each test run creates a folder named after the EFS reference:

```
output/
├── EFS123456/
│   ├── stage1_submitted.png
│   ├── pcm_stage_submitted.png
│   └── rd_stage_submitted.png
├── EFS123457/
│   ├── stage1_submitted.png
│   ├── pcm_stage_submitted.png
│   └── rd_stage_submitted.png
└── ...
```

## Contents

Each folder contains:
- **stage1_submitted.png** - Screenshot after Stage 1 (Inputter) submission
- **pcm_stage_submitted.png** - Screenshot after PCM approval
- **rd_stage_submitted.png** - Screenshot after RD approval

## Notes

- This directory is excluded from Git (see `.gitignore`)
- Folders are created automatically during test runs
- You can safely delete old test outputs to free up space
