# Building Android App on Low-Spec PCs

This guide helps you build the Rider Android app on computers with limited resources (low RAM, slower CPU).

## Problem

Android app compilation can freeze or crash on low-spec PCs due to high memory usage by Gradle and the Android build tools.

## Solution

We've optimized the build configuration to work better on low-spec machines. The following optimizations have been applied:

### 1. Reduced Memory Usage

**Before**: Gradle used up to 2GB RAM  
**After**: Gradle limited to 1GB RAM with optimized settings

The `gradle.properties` file now includes:
- Lower maximum heap size (1024m instead of 2048m)
- Efficient memory allocation
- Build cache enabled for faster rebuilds

### 2. Parallel Processing with Limited Workers

- Gradle uses only 2 parallel workers (prevents overwhelming the CPU)
- Incremental builds enabled
- File system watching for faster syncs

### 3. Faster Debug Builds

- PNG crunching disabled for debug builds (faster compilation)
- Pre-dexing enabled (reuses processed libraries)
- Optimized annotation processing (Kapt)

## Minimum Requirements

- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 10GB free space
- **Java**: Java 17 or higher
- **Android Studio**: Latest version (or build via command line)

## Building the App

### Option 1: Command Line (Recommended for Low-Spec PCs)

```bash
cd rider-app

# Clean build (first time or after major changes)
./gradlew clean assembleDebug

# Incremental build (much faster)
./gradlew assembleDebug
```

**Tips for Low-Spec PCs:**
1. Close unnecessary applications before building
2. Use `assembleDebug` instead of running in Android Studio
3. Don't run multiple Gradle tasks simultaneously
4. Let the Gradle daemon stay running between builds (faster subsequent builds)

### Option 2: Using Docker (Best for Very Low-Spec PCs)

If your PC still struggles, use Docker to offload the build process:

```bash
cd /path/to/AnomaaH-
./build-apk.sh
```

This uses Docker container to build the app, which can be more efficient on some systems.

## Build Time Expectations

On a low-spec PC (4GB RAM, dual-core CPU):

- **First build**: 10-15 minutes
- **Clean build**: 8-12 minutes  
- **Incremental build**: 2-5 minutes (after small code changes)
- **No-op build**: 30-60 seconds (no changes)

## Troubleshooting

### Build Freezes or Crashes

**Symptom**: Build hangs, PC becomes unresponsive, or "Out of Memory" errors

**Solutions**:

1. **Further reduce memory**:
   Edit `rider-app/gradle.properties`:
   ```properties
   org.gradle.jvmargs=-Xmx768m -Xms256m ...
   ```

2. **Disable parallel builds**:
   Edit `rider-app/gradle.properties`:
   ```properties
   org.gradle.parallel=false
   ```

3. **Close Android Studio**: Build from command line instead
   ```bash
   cd rider-app
   ./gradlew assembleDebug --no-daemon
   ```

### Build is Too Slow

**Solutions**:

1. **Enable Gradle daemon** (already enabled in optimized config)
2. **Use incremental builds**: Don't run `clean` unless necessary
3. **Enable build cache**: Already enabled, but you can clear it if corrupted:
   ```bash
   ./gradlew cleanBuildCache
   ```

### Daemon Uses Too Much Memory

If the Gradle daemon stays in memory and causes issues:

```bash
# Stop the daemon after building
./gradlew --stop

# Or disable daemon completely (slower builds)
./gradlew assembleDebug --no-daemon
```

## Advanced Optimization

For very low-spec machines (2-3GB RAM), you can:

1. **Further reduce Gradle memory**:
   Edit `rider-app/gradle.properties`:
   ```properties
   org.gradle.jvmargs=-Xmx768m -Xms256m ...
   org.gradle.workers.max=1
   ```

2. **Disable build features you don't need**:
   Already optimized in `gradle.properties`

3. **Use command line instead of Android Studio**:
   Android Studio itself uses 1-2GB RAM. Building from command line saves memory.

## Cloud Build Alternative

If your PC still struggles, consider using:

1. **GitHub Actions**: Automated builds in the cloud (free for public repos)
2. **Google Cloud Build**: Cloud-based compilation
3. **Remote development**: Use a cloud VM for building

## Monitoring Build Performance

Track your build performance:

```bash
# Add to command to see build timing
./gradlew assembleDebug --profile

# Report saved to: build/reports/profile/
```

## Questions?

If you continue experiencing issues:
1. Check your Java version: `java -version` (must be Java 17+)
2. Check available RAM: Ensure you have at least 2GB free
3. Report issues with details about your PC specs

---

**Made with ❤️ for developers with any PC specs**
