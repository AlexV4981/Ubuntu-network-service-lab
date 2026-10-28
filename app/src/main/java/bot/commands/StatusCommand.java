package bot.commands;

import bot.services.MinecraftService;
import net.dv8tion.jda.api.events.interaction.command.SlashCommandInteractionEvent;

public class StatusCommand implements Command {

    private final MinecraftService minecraftService;

    public StatusCommand(MinecraftService minecraftService) {
        this.minecraftService = minecraftService;
    }

    @Override
    public String getName() {
        return "status";
    }

    @Override
    public void execute(SlashCommandInteractionEvent event) {

        String response = minecraftService.getStatus(
                event.getUser().getId(),
                event.getUser().getName()
        );

        event.reply(response).queue();
    }
}
