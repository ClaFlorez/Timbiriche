# Timbiriche con Tutu — Windows Installation

## Run from source

Requirements:

- Flutter with Dart 3.10 or later.
- Visual Studio with the **Desktop development with C++** workload.

```powershell
git clone https://github.com/ClaFlorez/Timbiriche.git
cd Timbiriche
flutter pub get
flutter run -d windows
```

Online rooms require a local Firebase configuration generated with:

```powershell
dart pub global activate flutterfire_cli
flutterfire configure
```

## Build a distributable version

```powershell
flutter build windows --release
```

The application bundle will be generated under:

```text
build\windows\x64\runner\Release\
```

Distribute the complete `Release` folder, not only the executable, because the application also requires the adjacent DLL and data files.

## Windows security notice

Unsigned builds can trigger Microsoft Defender SmartScreen. For public distribution, sign the installer or executable with a trusted code-signing certificate.
