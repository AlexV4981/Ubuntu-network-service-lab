package bot.services;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class MinecraftService {

    private final HttpClient client;
    private final String controllerUrl;


    public MinecraftService() {

        this.client = HttpClient.newHttpClient();
        this.controllerUrl = "http://minecraft-controller:5000";

    }



    private String sendRequest(
            String method,
            String endpoint,
            String userId,
            String username
    ) {

        try {

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(controllerUrl + endpoint))
                    .header("X-User-ID", userId)
                    .header("X-User", username)
                    .method(
                            method,
                            HttpRequest.BodyPublishers.noBody()
                    )
                    .build();



            HttpResponse<String> response =
                    client.send(
                            request,
                            HttpResponse.BodyHandlers.ofString()
                    );


            return response.body();



        } catch (Exception e) {

            return """
                    {
                      "error": "Controller unreachable"
                    }
                    """;
        }
    }


public String getStatus(
        String userId,
        String username
) {

    return sendRequest(
            "GET",
            "/status",
            userId,
            username
    );

}



    public String startServer(
            String userId,
            String username
    ) {

        return sendRequest(
                "POST",
                "/up",
                userId,
                username
        );

    }



    public String stopServer(
            String userId,
            String username
    ) {

        return sendRequest(
                "POST",
                "/down",
                userId,
                username
        );

    }



    public String restartServer(
            String userId,
            String username
    ) {

        return sendRequest(
                "POST",
                "/restart",
                userId,
                username
        );

    }
}
