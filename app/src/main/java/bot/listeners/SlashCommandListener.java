package bot.listeners;

import bot.commands.Command;
import bot.commands.PingCommand;
import bot.commands.StatusCommand;
import bot.commands.UpCommand;
import bot.commands.DownCommand;
import bot.commands.RestartCommand;

import bot.services.MinecraftService;
import bot.services.PermissionService;

import net.dv8tion.jda.api.events.interaction.command.SlashCommandInteractionEvent;
import net.dv8tion.jda.api.hooks.ListenerAdapter;

import java.util.HashMap;
import java.util.Map;

public class SlashCommandListener extends ListenerAdapter {

    private final Map<String, Command> commands = new HashMap<>();


    public SlashCommandListener(
            MinecraftService minecraftService,
            PermissionService permissionService
    ) {


        commands.put(
                "ping",
                new PingCommand()
        );


        commands.put(
                "status",
                new StatusCommand(minecraftService)
        );


        commands.put(
                "up",
                new UpCommand(
                        minecraftService,
                        permissionService
                )
        );


        commands.put(
                "down",
                new DownCommand(
                        minecraftService,
                        permissionService
                )
        );


        commands.put(
                "restart",
                new RestartCommand(
                        minecraftService,
                        permissionService
                )
        );

    }


    @Override
    public void onSlashCommandInteraction(
            SlashCommandInteractionEvent event
    ) {

        Command command = commands.get(event.getName());

        if (command != null) {
            command.execute(event);
        }
    }
}
