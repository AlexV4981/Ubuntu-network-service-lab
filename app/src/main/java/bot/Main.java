package bot;

import bot.listeners.SlashCommandListener;
import bot.services.MinecraftService;
import bot.services.PermissionService;

import net.dv8tion.jda.api.JDA;
import net.dv8tion.jda.api.JDABuilder;

public class Main {

    public static void main(String[] args) throws Exception {

        String token = System.getenv("DISCORD_TOKEN");

        if (token == null) {
            throw new IllegalStateException("Missing DISCORD_TOKEN");
        }


        String guildId = System.getenv("DISCORD_GUILD_ID");

        if (guildId == null) {
            throw new IllegalStateException("Missing DISCORD_GUILD_ID");
        }


        String controlRoleId = System.getenv("MC_CONTROL_ROLE_ID");

        if (controlRoleId == null) {
            throw new IllegalStateException("Missing MC_CONTROL_ROLE_ID");
        }


        MinecraftService minecraftService =
                new MinecraftService();


        PermissionService permissionService =
                new PermissionService(controlRoleId);



        JDA jda = JDABuilder
                .createDefault(token)
                .addEventListeners(
                        new SlashCommandListener(
                                minecraftService,
                                permissionService
                        )
                )
                .build();


        jda.awaitReady();


        System.out.println("Registering guild commands...");


        var guild = jda.getGuildById(guildId);


        if (guild == null) {
            throw new IllegalStateException("Guild not found");
        }



        guild.upsertCommand(
                "ping",
                "Check if the bot is alive"
        ).queue();


        guild.upsertCommand(
                "status",
                "Shows Minecraft server status"
        ).queue();


        guild.upsertCommand(
                "up",
                "Start Minecraft server"
        ).queue();


        guild.upsertCommand(
                "down",
                "Stop Minecraft server"
        ).queue();


        guild.upsertCommand(
                "restart",
                "Restart Minecraft server"
        ).queue();



        System.out.println("Helpy bot is online!");



        Runtime.getRuntime().addShutdownHook(new Thread(() -> {

            System.out.println("Helpy shutting down...");
            jda.shutdown();

        }));
    }
}
