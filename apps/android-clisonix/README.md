# Clisonix Android App (Ocean + Posta Links)

Ky modul është scaffold Android për Clisonix me:

- Ocean Curiosity si hyrje kryesore
- Posta Links (`clisonix://module/...`) për navigim ndërmjet moduleve
- Kotlin + Jetpack Compose + Navigation
- Retrofit client për endpoint-in real `https://api.clisonix.com/v1/ocean-curiosity`
- Room cache lokale për payload-in e fundit të Ocean
- Endpoint health monitor për modulet kryesore (HTTP status + timestamp)

## Struktura

- `app/src/main/java/com/clisonix/app/navigation`: router + nav graph
- `app/src/main/java/com/clisonix/app/ui/screens`: ekranet Compose
- `app/src/main/java/com/clisonix/app/data`: API client
- `app/src/main/assets/posta_registry.json`: registry i moduleve

## Build

Nga folderi `apps/android-clisonix`:

```bash
./gradlew assembleDebug
```

Në Windows PowerShell:

```powershell
.\gradlew.bat assembleDebug
```

## Build Kur Mungon Java/Gradle Lokal

Nëse host-i nuk ka `java`, `gradle` ose `gradlew.bat`, përdor container-in e izoluar Android:

```powershell
docker compose -f docker-compose.android.yml run --rm android-build
```

Ky command kryen automatikisht:

- `gradle wrapper --gradle-version 8.7`
- `./gradlew clean`
- `./gradlew assembleDebug`

Për testet unit në container të izoluar:

```powershell
docker compose -f docker-compose.android.yml run --rm android-test
```

Ky command kryen automatikisht:

- `gradle wrapper --gradle-version 8.7`
- `./gradlew testDebugUnitTest`

## CI (Android Vetëm)

Workflow i dedikuar për Android ndodhet te `.github/workflows/android-clisonix-ci.yml` dhe aktivizohet vetëm kur preken skedarët në `apps/android-clisonix/**`.

## Test i Deep Link

```bash
adb shell am start -W -a android.intent.action.VIEW -d "clisonix://module/neural" com.clisonix.app
```
