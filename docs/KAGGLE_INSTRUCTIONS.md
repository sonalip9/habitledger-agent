# Running HabitLedger on Kaggle

This guide explains how to run the HabitLedger demo notebook on Kaggle.

## Prerequisites

1. A Kaggle account
2. A Google API key for Gemini (get one at [Google AI Studio](https://aistudio.google.com/app/apikey))

## Step 1: Upload the Repository as a Kaggle Dataset

1. Go to [Kaggle Datasets](https://www.kaggle.com/datasets) and click **+ New Dataset**
2. Upload the entire `habitledger-agent` repository folder
3. Name the dataset `habitledger-agent`
4. Set visibility to **Private** (recommended) or **Public**
5. Click **Create**

**Alternative**: If you only want to run the demo without full source access:
- Upload just the `src/` folder and `data/behaviour_principles.json` file

## Step 2: Configure Your API Key

1. Open any Kaggle notebook
2. Click **Add-ons** in the top menu
3. Select **Secrets**
4. Click **Add a new secret**
5. Set:
   - **Label**: `GOOGLE_API_KEY`
   - **Value**: Your Google API key
6. Click **Save**

> ⚠️ **Security Note**: Kaggle Secrets are encrypted and only accessible by you. Never paste your API key directly in notebook code.

## Step 3: Create and Run the Notebook

### Option A: Upload the Demo Notebook

1. Go to **Kaggle** → **Code** → **+ New Notebook**
2. Click **File** → **Import Notebook**
3. Upload `notebooks/demo.ipynb` from the repository

### Option B: Create a New Notebook

1. Create a new notebook on Kaggle
2. Add the `habitledger-agent` dataset:
   - Click **+ Add Data** on the right panel
   - Search for your uploaded dataset
   - Click **Add**

## Step 4: Enable Dependencies

In the first code cell of your notebook, uncomment and run the dependency installation:

```python
# Uncomment the following line to install dependencies
install_dependencies()
```

## Step 5: Run the Notebook

Execute cells in order. The notebook will:

1. Detect the Kaggle environment automatically
2. Load the API key from Kaggle Secrets
3. Find data files from the attached dataset
4. Run the HabitLedger demo

## Troubleshooting

### "Module not found" Error

Ensure the dataset is properly attached:
```python
import os
print(os.listdir("/kaggle/input/"))
```

You should see `habitledger-agent` in the output.

### "API key not found" Error

1. Verify your secret is named exactly `GOOGLE_API_KEY`
2. Re-add the secret and ensure there are no extra spaces
3. Restart the notebook kernel

### "Data file not found" Error

Check that `behaviour_principles.json` exists:
```python
import os
from pathlib import Path

# Check possible locations
paths = [
    "/kaggle/input/habitledger-agent/data/behaviour_principles.json",
    "/kaggle/input/habitledger-data/behaviour_principles.json",
]
for p in paths:
    print(f"{p}: {Path(p).exists()}")
```

### Reducing API Calls

If you're concerned about API quota:
1. In the evaluation cell, change `MAX_SCENARIOS = 20` to a lower number (e.g., 5)
2. This reduces the number of LLM calls during the comprehensive evaluation

## File Structure on Kaggle

After setup, your Kaggle environment will look like:

```
/kaggle/
├── input/
│   └── habitledger-agent/       # Your uploaded dataset
│       ├── src/                 # Source code
│       ├── data/                # Data files
│       └── ...
└── working/                     # Your notebook output
    └── demo.ipynb
```

## Memory Persistence

By default, memory is kept in-memory and not saved to files. If you need to save memory state:

```python
from src.config import get_working_directory

working_dir = get_working_directory()
memory_path = working_dir / "user_memory.json"
user_memory.save_to_file(str(memory_path))
print(f"Memory saved to {memory_path}")
```

## Additional Resources

- [HabitLedger Source Repository](https://github.com/sonalip9/habitledger-agent)
- [Google AI Studio](https://aistudio.google.com/) - For API key management
- [Kaggle Secrets Documentation](https://www.kaggle.com/docs/secrets)
