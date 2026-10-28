FROM maven:3.9-eclipse-temurin-21 AS build

WORKDIR /build

COPY app/pom.xml .

COPY app/src ./src

RUN mvn clean package


FROM eclipse-temurin:21-jre

WORKDIR /app

COPY --from=build /build/target/helpy-bot-1.0.jar /app/helpy-bot.jar

CMD ["java", "-jar", "/app/helpy-bot.jar"]
