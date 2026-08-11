# Problemas encontrados y soluciones

Este documento reúne los problemas encontrados al preparar y ejecutar Timbiriche con Tutu en Windows y Android.

## Windows: falta `flutter_windows.dll`

### Síntoma

Al abrir `timbiriche_flutter.exe`, Windows muestra:

```text
The code execution cannot proceed because flutter_windows.dll was not found.
```

### Causa

Se copió o distribuyó únicamente el archivo `.exe`. Una aplicación Flutter para Windows no funciona como un ejecutable aislado: también necesita `flutter_windows.dll`, las DLL de los plugins y la carpeta `data` generadas durante la compilación.

### Solución

```powershell
flutter build windows --release
```

Distribuir completa esta carpeta, preferiblemente dentro de un ZIP:

```text
build\windows\x64\runner\Release\
```

Después de extraer el ZIP, el `.exe` debe ejecutarse sin moverlo fuera de esa carpeta.

## PowerShell: `--stacktrace` produce un error de sintaxis

### Síntoma

PowerShell muestra `MissingExpressionAfterOperator` o indica que `stacktrace` es un token inesperado.

### Causa

`--stacktrace` es una opción de Gradle, no un comando independiente. PowerShell interpreta `--` como un operador cuando se escribe solo.

### Solución

Ejecutar la opción en la misma línea que Gradle:

```powershell
cd android
.\gradlew.bat assembleDebug --stacktrace
```

Para mostrar también todas las advertencias deprecadas:

```powershell
.\gradlew.bat assembleDebug --stacktrace --warning-mode all
```

## Android: Gradle falla mostrando solamente `25.0.2`

### Síntoma

La sección `What went wrong` muestra:

```text
25.0.2
```

También pueden aparecer advertencias sobre `java.lang.System::load` y acceso nativo restringido.

### Causa

Flutter o Android Studio está ejecutando Gradle con Java 25. Este proyecto y su configuración actual de Gradle deben compilarse con Java 17.

### Solución

Comprobar que Java 17 esté instalado y configurarlo explícitamente en Flutter:

```powershell
flutter config --jdk-dir "C:\Program Files\Java\jdk-17"
```

Cerrar y volver a abrir Android Studio después del cambio. En Android Studio también se puede seleccionar JDK 17 desde:

```text
File > Settings > Build, Execution, Deployment > Build Tools > Gradle
```

## Gradle intenta utilizar `C:\.gradle`

### Síntoma

Gradle no puede crear un archivo `.zip.lck` dentro de `C:\.gradle` o muestra acceso denegado.

### Causa

La carpeta de usuario de Gradle se resolvió incorrectamente como la raíz de la unidad `C:`.

### Solución

En la configuración de Gradle de Android Studio, establecer **Gradle user home** en:

```text
C:\Users\<USUARIO>\.gradle
```

No se debe guardar una ruta personal concreta dentro del repositorio.

## Paquetes con versiones más recientes

### Mensaje

```text
43 packages have newer versions incompatible with dependency constraints.
```

### Significado

No es un error. `flutter pub get` terminó correctamente y solo informa que existen versiones posteriores fuera de las restricciones actuales.

Consultar las actualizaciones con:

```powershell
flutter pub outdated
```

No ejecutar una actualización mayor automática sin revisar compatibilidad y volver a ejecutar las pruebas.

## Funciones de Gradle deprecadas

El mensaje que indica incompatibilidad futura con Gradle 9.0 es una advertencia, no necesariamente la causa de un `BUILD FAILED`. El error accionable suele aparecer antes, bajo `What went wrong` o `Execution failed for task`.

Para inspeccionar cada advertencia:

```powershell
cd android
.\gradlew.bat assembleDebug --warning-mode all --stacktrace
```

## Comprobación final

```powershell
flutter pub get
flutter run
```

Para generar el APK de entrega:

```powershell
flutter build apk --release
```

El APK se genera en:

```text
build\app\outputs\flutter-apk\app-release.apk
```
