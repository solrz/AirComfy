# AirComfy iOS App

Clean iOS wrapper for the AirComfy PWA with CORS proxy capabilities.

## Structure

```
ios-app/
├── Sources/           # Swift source files
├── Resources/         # Assets, manifest.json, etc.
├── Tests/            # Unit and UI tests
└── Project/          # Essential Xcode project files
```

## Build

1. Open in Xcode: `xed ios-app/`
2. Select target device/simulator
3. Build and run

## Features

- WebKit wrapper for AirComfy PWA
- CORS proxy via URL scheme handler
- Embedded web resources
- Native iOS app bundle