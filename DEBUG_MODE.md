# Debug Mode Configuration

AirComfy now includes a debug mode for faster development and testing.

## Features

- **Auto-load Workflow**: Automatically loads a preset workflow when debug mode is enabled
- **Auto-load Endpoint**: Automatically selects and connects to a preset endpoint
- **Visual Indicator**: Shows "DEBUG" badge in header when debug mode is active
- **Persistent Settings**: Debug mode state is saved in localStorage

## Activation

### Via URL Parameter
Add `?debug=true` to the URL:
```
http://localhost:8000?debug=true
```

### Via UI Toggle
Click the "Enable Debug Mode" button in the Configuration section

## Usage

### First Time Setup
1. Load your frequently-used workflow
2. Select your development endpoint
3. Enable debug mode
4. Your current workflow and endpoint are saved as debug presets

### Subsequent Sessions
1. Access the app with `?debug=true`
2. The saved workflow and endpoint are automatically loaded
3. Auto-connects to the server after 500ms

## Debug Controls

When debug mode is active:
- **Debug Mode: ON** - Toggle debug mode off
- **Clear Debug Presets** - Remove saved workflow and endpoint

## Default Workflow

If no debug workflow is saved, a default SD1.5 text-to-image workflow is loaded with:
- Model: `v1-5-pruned-emaonly.safetensors`
- Positive prompt: "beautiful scenery nature glass bottle landscape, purple galaxy bottle"
- Negative prompt: "text, watermark"
- Image size: 512x512
- Steps: 20

## localStorage Keys

Debug mode uses the following localStorage keys:
- `aircomfy-settings`: Stores debug mode state
- `aircomfy-debug-workflow`: Stores the preset workflow JSON
- `aircomfy-debug-endpoint`: Stores the preset endpoint ID

## Testing

Run the debug mode test suite:
```bash
python3 test_debug_mode.py
```

This tests:
- Debug badge visibility
- Debug controls functionality
- Workflow preloading
- Endpoint preselection
- Debug mode toggling