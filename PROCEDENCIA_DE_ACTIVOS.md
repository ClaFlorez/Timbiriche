# Procedencia y licencias de activos

Este inventario documenta el origen conocido de las imágenes, sonidos y música incluidos en Timbiriche con Tutu. Los comprobantes privados —historiales de generación, recibos, suscripciones y archivos originales— deben conservarse fuera del repositorio.

## Estado de los activos

| Activo de la aplicación | Tipo | Origen | Estado documental |
| --- | --- | --- | --- |
| `assets/audio/cuadro_brillante.mp3` | Efecto de acierto | Derivado del efecto `Correct_answer_chime_#4-1786405841138.mp3`, generado con ElevenLabs Sound Effects v2 | Origen y plan confirmados; conservar evidencia privada |
| `assets/audio/joyful_bgm.mp3` | Música de fondo | Proyecto `Joyful Focus`, generado con ElevenLabs Music v1 | Origen y plan confirmados; conservar evidencia privada |
| `assets/images/app_icon_v2.png` | Icono e imagen principal | Canva junto con Gemini | Pendiente de registrar elementos, plan y comprobantes aplicables |

## Recursos históricos excluidos

- `assets/audio/magic_bgm.mp3` no se utiliza y no se declara en `pubspec.yaml`.
- El proyecto de ElevenLabs `Victoria ¡Yey!` no se utiliza ni forma parte de los archivos de la aplicación.
- `assets/video/mariposa-animada.mp4` corresponde a una versión anterior, no se referencia en el código, no se declara en `pubspec.yaml` y está excluido de Git.

Las mariposas visibles en la versión actual son animaciones programadas en `lib/magic_effects.dart` mediante el carácter emoji `🦋`; no utilizan el video histórico.

## Efecto de acierto de ElevenLabs

- Servicio: ElevenLabs Sound Effects v2.
- Prompt: `Bright, short video game point sound effect.`
- Variante seleccionada: número 4.
- Duración mostrada: 1.5 segundos.
- Archivo original: `Correct_answer_chime_#4-1786405841138.mp3`.
- SHA-256 del original: `EE06ECD079BA3641CB03ED8748985AA21EBCE03842EEFC97FBA9A5A65F082DBB`.
- Plan mostrado al momento de aportar la evidencia: Starter, con saldo de créditos.
- Uso en la aplicación: efecto reproducido al completar un cuadro.
- Transformación: el archivo incorporado como `cuadro_brillante.mp3` no es idéntico byte por byte al original; debe conservarse también cualquier registro de edición o conversión.

El plan Starter es un plan pagado. ElevenLabs indica que los contenidos generados durante planes pagados pueden utilizarse comercialmente, sujeto a sus términos, a que el contenido no provenga de un servicio beta y a que la persona usuaria posea los derechos necesarios. Las condiciones vigentes al momento de cada generación deben conservarse junto con el comprobante de suscripción.

Referencia oficial: <https://help.elevenlabs.io/hc/en-us/articles/13313564601361-Can-I-publish-the-content-I-generate-on-the-platform>

## Música de fondo de ElevenLabs

- Servicio: ElevenLabs Music v1.
- Nombre del proyecto: `Joyful Focus`.
- Descripción visible: instrumental, ambient, background music.
- Duración mostrada en el historial: 1:25.
- Archivo incorporado: `assets/audio/joyful_bgm.mp3`.
- Duración técnica del archivo incorporado: 1:25.
- SHA-256: `7AB0E095857FEACC1B085C04FFF87B6AD1D55A18A39BCF7E9B50FA31A8441E9E`.
- Plan mostrado al momento de aportar la evidencia: Starter.
- Uso en la aplicación: música ambiental de fondo.

La coincidencia de nombre y duración vincula el proyecto mostrado en el historial con el archivo incorporado. Debe conservarse de forma privada la captura del historial y el comprobante del plan pagado.

El historial también muestra un proyecto llamado `Victoria ¡Yey!` de 0:15 y existe localmente un archivo llamado `magic_bgm.mp3` de 2:13. La responsable confirmó que ninguno de los dos se utiliza en la aplicación. `pubspec.yaml` enumera individualmente los dos audios utilizados para impedir que otros archivos locales de la carpeta se incorporen accidentalmente a los paquetes de distribución.

## Evidencia que debe conservarse de forma privada

- Captura del historial que muestra el prompt y la variante número 4.
- Captura o factura que demuestra el plan Starter.
- Archivo original descargado.
- Fecha de generación y condiciones de ElevenLabs vigentes en esa fecha.
- Registro de cualquier edición, recorte o conversión aplicada.
- Proyecto y exportación de Canva, junto con la información de licencia de cada elemento utilizado.
- Historial o comprobantes de Gemini asociados con la imagen.

Este documento es un registro técnico y no sustituye asesoramiento jurídico profesional.
