# 03 — Java & JVM Languages (Examples 31–40)

[⬅️ Back to Handbook Index](README.md) · [⬅️ Previous: Python](02-python.md)

---

## 🧾 What is Java? (for non-developers)

- **Java** is a compiled language used heavily in enterprises (banks, insurance, big
  backends). **Kotlin** and **Scala** are other languages that run on the same engine.
- Java code is compiled into **bytecode** packaged as a **`.jar`** file ("Java ARchive")
  or a **`.war`** file (for traditional app servers like Tomcat).
- A jar doesn't run on its own — it needs the **JVM** (Java Virtual Machine).
- **JDK** (Java Development Kit) = compiler + JVM (~400 MB) → needed to **build**.
- **JRE** (Java Runtime Environment) = just the JVM (~150 MB) → enough to **run**.
- **Build tools:** **Maven** (`pom.xml`) or **Gradle** (`build.gradle` / `build.gradle.kts`).
  Projects often include a **wrapper** script (`mvnw` / `gradlew`) that downloads the
  correct tool version automatically.
- **Spring Boot** is the dominant Java web framework. It produces a "fat jar" (app + all
  dependencies in one file) that runs with `java -jar app.jar`.

### Which base image?

| Image | Contains | Use for |
|-------|----------|---------|
| `maven:3.9-eclipse-temurin-21` | Maven + JDK 21 | **Build** stage (Maven) |
| `gradle:8-jdk21` | Gradle + JDK 21 | **Build** stage (Gradle) |
| `eclipse-temurin:21-jdk` | JDK 21 | Build stage with wrapper scripts |
| `eclipse-temurin:21-jre` / `21-jre-alpine` | JRE 21 | **Runtime** stage |
| `gcr.io/distroless/java21-debian12` | JRE, no shell | Hardened runtime |

> **Eclipse Temurin** is a free, widely-used build of OpenJDK. Other good choices:
> Amazon Corretto, Microsoft Build of OpenJDK, Azul Zulu. Pick one and standardise.

> Use **LTS** Java versions in production: **17, 21, 25**.

### ⚠️ The #1 Java-in-containers gotcha: memory

The JVM decides its maximum heap size (memory for objects) based on available RAM. Old
JVMs (before Java 10 / 8u191) looked at the **host's** RAM, not the container limit →
the container gets **OOMKilled** (killed for exceeding its memory limit).

Modern JVMs *are* container-aware, but by default use only **25%** of the container's
memory for heap — wasteful. Always set:

```dockerfile
ENV JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=75.0 -XX:+ExitOnOutOfMemoryError"
```

- `MaxRAMPercentage=75` — heap can use 75% of the container limit (rest for threads,
  metaspace, native memory).
- `ExitOnOutOfMemoryError` — if memory runs out, **crash** instead of limping along in a
  broken state. The orchestrator restarts it cleanly.
- `JAVA_TOOL_OPTIONS` is read automatically by every JVM — no need to change the start command.

### Starter `.dockerignore` for Java

```gitignore
target/
build/
.gradle/
.idea/
*.iml
.git
.env*
Dockerfile*
.dockerignore
```

---

## Table of Contents

| # | Example | Key idea |
|---|---------|----------|
| 31 | [Spring Boot + Maven, multi-stage](#example-31--spring-boot--maven-multi-stage) | The baseline Java Dockerfile |
| 32 | [Spring Boot + Gradle](#example-32--spring-boot--gradle) | Gradle wrapper + cache |
| 33 | [Spring Boot layered jar](#example-33--spring-boot-layered-jar) | Faster pushes/pulls |
| 34 | [Custom slim JRE with jlink](#example-34--custom-slim-jre-with-jlink) | Ship only needed Java modules |
| 35 | [Runtime-only image (jar built by CI)](#example-35--runtime-only-image-jar-built-by-ci) | When the pipeline already built the jar |
| 36 | [Quarkus (JVM mode)](#example-36--quarkus-jvm-mode) | Cloud-native Java framework |
| 37 | [Quarkus native (GraalVM)](#example-37--quarkus-native-graalvm) | Java compiled to a native binary |
| 38 | [Tomcat + WAR](#example-38--tomcat--war) | Legacy app server |
| 39 | [Kotlin + Ktor](#example-39--kotlin--ktor) | Kotlin fat jar |
| 40 | [Distroless Java](#example-40--distroless-java) | Hardened runtime |

---

## Example 31 — Spring Boot + Maven, multi-stage

**📁 Developer gives you:** `pom.xml`, `src/main/java/...`. Build output: `target/*.jar`.

```dockerfile
# syntax=docker/dockerfile:1

########## Stage 1: build with Maven + JDK ##########
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /build

# 1) Copy only pom.xml and download dependencies (cached until pom.xml changes)
COPY pom.xml .
RUN --mount=type=cache,target=/root/.m2 \
    mvn -B dependency:go-offline

# 2) Copy source and build the jar (skip tests here; run them in CI separately)
COPY src ./src
RUN --mount=type=cache,target=/root/.m2 \
    mvn -B package -DskipTests \
 && cp target/*.jar app.jar

########## Stage 2: run with JRE only ##########
FROM eclipse-temurin:21-jre-jammy AS runtime

RUN groupadd --system --gid 1001 spring \
 && useradd --system --uid 1001 --gid spring --no-create-home spring

WORKDIR /app
COPY --from=build --chown=1001:1001 /build/app.jar app.jar

ENV JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=75.0 -XX:+ExitOnOutOfMemoryError"

USER 1001
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

**🔍 Explained:**

- `mvn -B` — "batch mode": no colours/interactive prompts; cleaner CI logs.
- `dependency:go-offline` — downloads all dependencies up front so the next layer can be cached.
- `--mount=type=cache,target=/root/.m2` — Maven's local repository (`~/.m2`) persists across builds.
- `cp target/*.jar app.jar` — normalises the jar name (`myservice-1.4.2-SNAPSHOT.jar` →
  `app.jar`) so the runtime stage doesn't need to know the version.
- `-jre-jammy` — JRE on Ubuntu 22.04. ~200 MB vs ~500 MB for the full JDK.

**⚠️ DevOps Gotchas:**

- `cp target/*.jar` fails if there are **two** jars (Spring Boot also produces
  `*-plain.jar` in some configurations). Disable the plain jar in the build config, or
  copy the exact name.
- `dependency:go-offline` doesn't always catch plugin dependencies; the package step may
  still download some. The cache mount covers that.
- **Spring Boot Actuator** gives you `/actuator/health/liveness` and
  `/actuator/health/readiness` for Kubernetes probes — ask devs to enable it.

---

## Example 32 — Spring Boot + Gradle

**📁 Developer gives you:** `build.gradle(.kts)`, `settings.gradle(.kts)`, `gradlew`,
`gradle/wrapper/`, `src/`. Output: `build/libs/*.jar`.

```dockerfile
# syntax=docker/dockerfile:1
FROM eclipse-temurin:21-jdk-jammy AS build
WORKDIR /build

# Wrapper + build scripts first (for dependency caching)
COPY gradlew settings.gradle* build.gradle* ./
COPY gradle ./gradle
RUN chmod +x gradlew
RUN --mount=type=cache,target=/root/.gradle \
    ./gradlew dependencies --no-daemon > /dev/null

COPY src ./src
RUN --mount=type=cache,target=/root/.gradle \
    ./gradlew bootJar --no-daemon -x test \
 && cp build/libs/*.jar app.jar

FROM eclipse-temurin:21-jre-jammy
RUN useradd --system --uid 1001 --no-create-home spring
WORKDIR /app
COPY --from=build --chown=1001:1001 /build/app.jar app.jar
ENV JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=75.0 -XX:+ExitOnOutOfMemoryError"
USER 1001
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

**🔍 Explained:**

- `settings.gradle*` — the `*` matches both `settings.gradle` and `settings.gradle.kts`.
- `chmod +x gradlew` — the wrapper often loses its execute bit when committed from Windows.
- `--no-daemon` — Gradle normally starts a background helper process; pointless in a one-shot build.
- `bootJar` — Spring Boot's Gradle task that builds the runnable fat jar.
- `-x test` — exclude the `test` task.

**⚠️ DevOps Gotchas:**

- `gradlew` with CRLF line endings → `/bin/sh^M: bad interpreter`. `.gitattributes`:
  `gradlew text eol=lf`.

---

## Example 33 — Spring Boot layered jar

**🧾 What is this?** A fat jar is one big file (~80 MB). Change one line of code → the
whole 80 MB layer changes → every deploy pushes/pulls 80 MB. Spring Boot can **split** the
jar into layers: dependencies (rarely change) vs your code (changes every commit).

```dockerfile
# syntax=docker/dockerfile:1
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /build
COPY pom.xml .
RUN --mount=type=cache,target=/root/.m2 mvn -B dependency:go-offline
COPY src ./src
RUN --mount=type=cache,target=/root/.m2 mvn -B package -DskipTests \
 && cp target/*.jar app.jar

# Extract the jar into layer folders (Spring Boot 3.3+ "tools" jarmode)
FROM eclipse-temurin:21-jre-jammy AS extract
WORKDIR /extract
COPY --from=build /build/app.jar app.jar
RUN java -Djarmode=tools -jar app.jar extract --layers --launcher --destination layers

FROM eclipse-temurin:21-jre-jammy AS runtime
RUN useradd --system --uid 1001 --no-create-home spring
WORKDIR /app
# Order: least-changing first → most-changing last
COPY --from=extract --chown=1001:1001 /extract/layers/dependencies/          ./
COPY --from=extract --chown=1001:1001 /extract/layers/spring-boot-loader/    ./
COPY --from=extract --chown=1001:1001 /extract/layers/snapshot-dependencies/ ./
COPY --from=extract --chown=1001:1001 /extract/layers/application/           ./
ENV JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=75.0 -XX:+ExitOnOutOfMemoryError"
USER 1001
EXPOSE 8080
ENTRYPOINT ["java", "org.springframework.boot.loader.launch.JarLauncher"]
```

**🔍 Explained:**

- `-Djarmode=tools ... extract --layers --launcher` — splits the jar into 4 folders.
- Four `COPY` lines = four image layers. A code change only modifies the small
  `application` layer (often < 1 MB). Registry pushes and node pulls become **much** faster.
- `JarLauncher` — Spring Boot's launcher class that runs the extracted app.

**⚠️ DevOps Gotchas:**

- **Spring Boot 2.x / 3.0–3.2** use the older syntax:
  `java -Djarmode=layertools -jar app.jar extract` and launcher class
  `org.springframework.boot.loader.JarLauncher` (no `.launch.`). Check the Spring Boot version
  in `pom.xml` before copying.

---

## Example 34 — Custom slim JRE with jlink

**🧾 What is this?** Java is split into **modules** (`java.base`, `java.sql`, `java.xml`…).
**jlink** builds a custom mini-JRE containing **only** the modules your app needs.
Result: JRE of ~50–70 MB instead of ~150+ MB.

```dockerfile
# syntax=docker/dockerfile:1
FROM eclipse-temurin:21-jdk-jammy AS jre-build
# Build a minimal Java runtime with only the modules we need
RUN jlink \
      --add-modules java.base,java.logging,java.naming,java.net.http,java.sql,java.management,java.instrument,java.security.jgss,java.desktop,jdk.crypto.ec,jdk.unsupported \
      --strip-debug \
      --no-man-pages \
      --no-header-files \
      --compress=zip-6 \
      --output /opt/jre

FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /build
COPY pom.xml .
RUN --mount=type=cache,target=/root/.m2 mvn -B dependency:go-offline
COPY src ./src
RUN --mount=type=cache,target=/root/.m2 mvn -B package -DskipTests && cp target/*.jar app.jar

# Plain Debian — no Java at all — plus our custom JRE
FROM debian:bookworm-slim
ENV JAVA_HOME=/opt/jre \
    PATH="/opt/jre/bin:$PATH" \
    JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=75.0 -XX:+ExitOnOutOfMemoryError"
COPY --from=jre-build /opt/jre /opt/jre
RUN useradd --system --uid 1001 --no-create-home app
WORKDIR /app
COPY --from=build --chown=1001:1001 /build/app.jar app.jar
USER 1001
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

**🔍 Explained:**

- `--add-modules` — the list of modules to include. You can discover them with
  `jdeps --print-module-deps --ignore-missing-deps app.jar` (needs extra flags for Spring
  fat jars).
- `--strip-debug`, `--no-man-pages`, `--no-header-files` — remove things not needed to run.
- `--compress=zip-6` — compress the runtime (JDK 21+ syntax; older JDKs used `--compress=2`).
- Runtime stage is plain `debian:bookworm-slim` — no Java installed; we bring our own.

**⚠️ DevOps Gotchas:**

- A **missing module** only fails at **runtime** with `ClassNotFoundException` /
  `NoClassDefFoundError` — sometimes only on a rarely-used code path (e.g. TLS → needs
  `jdk.crypto.ec`). Smoke-test thoroughly. If unsure, the standard JRE is the safer choice.
- Build the JRE on the **same OS family** (glibc) as the runtime.

---

## Example 35 — Runtime-only image (jar built by CI)

**🧾 What is this?** Many pipelines (Azure DevOps, Jenkins) already run `mvn package` and
tests in an earlier step. The Dockerfile then just **packages** the existing jar.

```dockerfile
# syntax=docker/dockerfile:1
FROM eclipse-temurin:21-jre-alpine

# Path to the jar produced by the CI step (override with --build-arg)
ARG JAR_FILE=target/app.jar

RUN addgroup -S -g 1001 app && adduser -S -u 1001 -G app app
WORKDIR /app
COPY --chown=1001:1001 ${JAR_FILE} app.jar

ENV JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=75.0 -XX:+ExitOnOutOfMemoryError -XX:+UseG1GC" \
    SERVER_PORT=8080

USER 1001
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8080/actuator/health || exit 1
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

**🔍 Explained:**

- `ARG JAR_FILE` — lets the pipeline pass the path: `docker build --build-arg JAR_FILE=build/libs/svc.jar .`
- `addgroup -S` / `adduser -S` — Alpine syntax for system group/user.
- `--start-period=60s` — Java apps start slowly; don't count health failures during boot.

**⚠️ DevOps Gotchas:**

- `.dockerignore` must **not** exclude `target/` here (otherwise the jar is invisible).
  This is the opposite of Example 31 — keep a separate `.dockerignore` or use
  `Dockerfile.dockerignore` (BuildKit supports per-Dockerfile ignore files).
- Trade-off: the image is only as reproducible as the CI agent's JDK/Maven setup. The
  fully multi-stage approach (Example 31) is more self-contained.

---

## Example 36 — Quarkus (JVM mode)

**🧾 What is this?** **Quarkus** is a Java framework optimised for containers: fast
startup, low memory. Its build output is a folder, `target/quarkus-app/`, not a single jar.

```dockerfile
# syntax=docker/dockerfile:1
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /build
COPY pom.xml .
RUN --mount=type=cache,target=/root/.m2 mvn -B dependency:go-offline
COPY src ./src
RUN --mount=type=cache,target=/root/.m2 mvn -B package -DskipTests

FROM eclipse-temurin:21-jre-jammy
RUN useradd --system --uid 1001 --no-create-home app
WORKDIR /app
# Quarkus "fast-jar" layout — copy in order of change frequency
COPY --from=build --chown=1001:1001 /build/target/quarkus-app/lib/     ./lib/
COPY --from=build --chown=1001:1001 /build/target/quarkus-app/*.jar    ./
COPY --from=build --chown=1001:1001 /build/target/quarkus-app/app/     ./app/
COPY --from=build --chown=1001:1001 /build/target/quarkus-app/quarkus/ ./quarkus/
ENV JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=75.0 -Djava.util.logging.manager=org.jboss.logmanager.LogManager"
USER 1001
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/quarkus-run.jar"]
```

**🔍 Explained:** Same layering idea as Example 33: `lib/` (dependencies) rarely changes,
`app/` (your code) changes often. `quarkus-run.jar` is the launcher.

**⚠️ DevOps Gotchas:**

- Quarkus generates sample Dockerfiles in `src/main/docker/` — check them; teams often
  already have one.
- Health endpoints come from the `smallrye-health` extension: `/q/health/live`, `/q/health/ready`.

---

## Example 37 — Quarkus native (GraalVM)

**🧾 What is this?** **GraalVM native image** compiles Java **ahead of time** into a native
Linux binary — no JVM needed. Starts in milliseconds, uses far less memory. Build is
**slow** (minutes) and memory-hungry (needs ~6–8 GB RAM).

```dockerfile
# syntax=docker/dockerfile:1
# Mandrel = a GraalVM distribution maintained for Quarkus
FROM quay.io/quarkus/ubi-quarkus-mandrel-builder-image:jdk-21 AS build
WORKDIR /code
COPY --chown=quarkus:quarkus mvnw pom.xml ./
COPY --chown=quarkus:quarkus .mvn ./.mvn
RUN ./mvnw -B dependency:go-offline
COPY --chown=quarkus:quarkus src ./src
RUN ./mvnw -B package -Dnative -DskipTests

# Tiny runtime image designed for Quarkus native binaries
FROM quay.io/quarkus/quarkus-micro-image:2.0
WORKDIR /work
COPY --from=build --chown=1001:root --chmod=0755 /code/target/*-runner /work/application
USER 1001
EXPOSE 8080
ENTRYPOINT ["./application", "-Dquarkus.http.host=0.0.0.0"]
```

**🔍 Explained:**

- `-Dnative` — tells Quarkus to produce a native executable (`target/<name>-runner`).
- The builder image runs as user `quarkus`, so copied files must be owned by it (`--chown=quarkus:quarkus`).
- `--chown=1001:root` + group-writable perms — a convention for **OpenShift**, which runs
  containers with random UIDs in the `root` group.
- Final image is often **< 100 MB** and starts in < 0.1 s.

**⚠️ DevOps Gotchas:**

- CI agents with 2–4 GB RAM will fail with "Exit code 137" (out of memory) during native
  builds. Use bigger agents.
- Native image doesn't support every Java library (reflection-heavy ones need config).
  It must be tested — not just flipped on by DevOps.
- `MaxRAMPercentage` doesn't apply (there's no JVM). Use `-Xmx` at runtime if needed.

---

## Example 38 — Tomcat + WAR

**🧾 What is this?** Older Java apps are packaged as **`.war`** files and deployed into an
**application server** like **Apache Tomcat**. Tomcat is the web server; the WAR is the app.

```dockerfile
# syntax=docker/dockerfile:1
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /build
COPY pom.xml .
RUN --mount=type=cache,target=/root/.m2 mvn -B dependency:go-offline
COPY src ./src
RUN --mount=type=cache,target=/root/.m2 mvn -B package -DskipTests

FROM tomcat:10.1-jre17-temurin-jammy

# Remove anything in webapps and deploy our app as ROOT (served at "/")
RUN rm -rf /usr/local/tomcat/webapps/* \
 && useradd --system --uid 1001 --no-create-home tomcat \
 && chown -R 1001:1001 /usr/local/tomcat/logs /usr/local/tomcat/temp \
      /usr/local/tomcat/work /usr/local/tomcat/webapps

COPY --from=build --chown=1001:1001 /build/target/*.war /usr/local/tomcat/webapps/ROOT.war

ENV CATALINA_OPTS="-XX:MaxRAMPercentage=75.0 -XX:+ExitOnOutOfMemoryError"

USER 1001
EXPOSE 8080
# The base image's default CMD is ["catalina.sh", "run"] — keep it
```

**🔍 Explained:**

- Naming the file `ROOT.war` → Tomcat serves it at `http://host:8080/` instead of `/myapp-1.0/`.
- Tomcat needs to **write** to `logs/`, `temp/`, `work/` and unpack the WAR in `webapps/`,
  so those folders are given to our user.
- `CATALINA_OPTS` — JVM options read by Tomcat's start script.
- No `CMD` needed — inherited from the base image.

**⚠️ DevOps Gotchas:**

- **Tomcat 10+ uses `jakarta.*`** packages; older apps built for **Tomcat 9 use `javax.*`**.
  Deploying an old WAR on Tomcat 10 = 404s and `ClassNotFoundException`. Match the version
  the app was built for (`tomcat:9.0-...`).
- Tomcat logs to files by default; configure it (or the app) to log to stdout for `docker logs`.

---

## Example 39 — Kotlin + Ktor

**🧾 What is this?** **Kotlin** is a modern JVM language (also used for Android). **Ktor**
is a Kotlin web framework. The Ktor Gradle plugin builds a fat jar with `buildFatJar`.

```dockerfile
# syntax=docker/dockerfile:1
FROM gradle:8-jdk21 AS build
WORKDIR /home/gradle/project
COPY --chown=gradle:gradle settings.gradle.kts build.gradle.kts gradle.properties* ./
COPY --chown=gradle:gradle gradle ./gradle
RUN --mount=type=cache,target=/home/gradle/.gradle,uid=1000,gid=1000 \
    gradle dependencies --no-daemon > /dev/null
COPY --chown=gradle:gradle src ./src
RUN --mount=type=cache,target=/home/gradle/.gradle,uid=1000,gid=1000 \
    gradle buildFatJar --no-daemon \
 && cp build/libs/*-all.jar app.jar

FROM eclipse-temurin:21-jre-alpine
RUN adduser -S -u 1001 app
WORKDIR /app
COPY --from=build --chown=1001 /home/gradle/project/app.jar app.jar
ENV JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=75.0 -XX:+ExitOnOutOfMemoryError"
USER 1001
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

**🔍 Explained:**

- `gradle:8-jdk21` — image with Gradle preinstalled (used here instead of the wrapper).
  It runs as user `gradle` (UID 1000), hence `--chown=gradle:gradle` and `uid=1000` on the
  cache mount.
- `gradle.properties*` — optional file; the `*` makes COPY not fail if it's missing
  (as long as another listed file matches).
- `*-all.jar` — Ktor/Shadow's naming for the fat jar.

**⚠️ DevOps Gotchas:**

- Using the `gradle` image's Gradle version instead of the project's wrapper can cause
  "unsupported Gradle version" errors. If the project has `gradlew`, prefer it (Example 32).

---

## Example 40 — Distroless Java

**🧾 What is this?** JRE only, no shell, runs as non-root by default.

```dockerfile
# syntax=docker/dockerfile:1
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /build
COPY pom.xml .
RUN --mount=type=cache,target=/root/.m2 mvn -B dependency:go-offline
COPY src ./src
RUN --mount=type=cache,target=/root/.m2 mvn -B package -DskipTests && cp target/*.jar app.jar

FROM gcr.io/distroless/java21-debian12:nonroot
WORKDIR /app
COPY --from=build --chown=65532:65532 /build/app.jar app.jar
ENV JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=75.0 -XX:+ExitOnOutOfMemoryError"
EXPOSE 8080
# The image ENTRYPOINT is ["java", "-jar"], so CMD is just the jar path
CMD ["app.jar"]
```

**🔍 Explained:**

- `java21-debian12:nonroot` — Java 21 runtime on Debian 12, user `nonroot` (65532).
- The distroless Java image's entrypoint is already `java -jar`, so we pass only the jar.

**⚠️ DevOps Gotchas:**

- No shell → `jcmd`, `jstack` heap/thread dumps via `docker exec` aren't available. Plan
  your production debugging story (ephemeral debug containers, JFR to a volume,
  `-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/dumps` with a mounted volume).

---

**Next:** [04 — Go, Rust, C/C++ ➡️](04-go-rust-c.md)
