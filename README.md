// index.js — Correio Elegante Bot (Discord.js v14)
const { Client, GatewayIntentBits, Partials, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, PermissionsBitField, ModalBuilder, TextInputBuilder, TextInputStyle } = require("discord.js");
require("dotenv").config();

const TOKEN = process.env.DISCORD_TOKEN;
const OWNER_ID = "974092488342118440"; // Seu ID

if (!TOKEN) {
  console.error("❌ Defina a variável DISCORD_TOKEN.");
  process.exit(1);
}

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
  ],
  partials: [Partials.Channel],
});

// ----- Estado -----
let canalCorreioId = null; // Onde as mensagens chegam
let canalPainelId = null;  // Onde o painel público aparece
let enviadosTotal = 0;

// ----- Utils -----
function isAdmin(member) {
  return member.permissions.has(PermissionsBitField.Flags.Administrator) || member.id === OWNER_ID;
}

// Mensagem do painel público
function painelEmbed() {
  return new EmbedBuilder()
    .setTitle("💌 CORREIO ELEGANTE 💌")
    .setColor(0xff4dd2)
    .setDescription(
      "💖 **Quer enviar uma mensagem especial para alguém?** 💖\n\n" +
      "> 🤫 *Escolha enviar de forma anônima ou revelar seu nome. Copie o @id da pessoa e escreva sua mensagem.*\n\n" +
      "🔒 **Sigilo absoluto garantido! Só você e o bot sabem.**\n\n" +
      "✨ **Clique em Anônimo ou Público e espalhe o amor (ou a trollagem)!** ✨"
    );
}

function escolhaRow() {
  return new ActionRowBuilder().addComponents(
    new ButtonBuilder()
      .setCustomId("correio_anonimo")
      .setLabel("Anônimo 🤫")
      .setStyle(ButtonStyle.Secondary),
    new ButtonBuilder()
      .setCustomId("correio_publico")
      .setLabel("Público 🪪")
      .setStyle(ButtonStyle.Primary)
  );
}

// Painel de administração
function painelAdminEmbed() {
  return new EmbedBuilder()
    .setTitle("🎛️ Painel de Administração — Correio Elegante")
    .setColor(0x57f287)
    .setDescription(
      `📢 **Canal de entrega:** ${canalCorreioId ? `<#${canalCorreioId}>` : "não definido"}\n` +
      `🎯 **Canal do painel:** ${canalPainelId ? `<#${canalPainelId}>` : "não definido"}\n` +
      `🧾 **Total enviados:** ${enviadosTotal}`
    );
}

function painelAdminRow() {
  return new ActionRowBuilder().addComponents(
    new ButtonBuilder()
      .setCustomId("painel_setarEntrega")
      .setLabel("Definir canal de entrega 📬")
      .setStyle(ButtonStyle.Primary),
    new ButtonBuilder()
      .setCustomId("painel_setarPainel")
      .setLabel("Definir canal do painel 📢")
      .setStyle(ButtonStyle.Success),
    new ButtonBuilder()
      .setCustomId("painel_info")
      .setLabel("Atualizar 🔄")
      .setStyle(ButtonStyle.Secondary)
  );
}

// ----- Boot -----
client.once("ready", async () => {
  console.log(`🤖 Logado como ${client.user.tag}`);
  client.user.setPresence({ activities: [{ name: "💌 Correio Elegante" }], status: "online" });

  // Registrar comando /painel
  await client.application.commands.set([
    { name: "painel", description: "Abrir painel de administração do Correio Elegante" }
  ]);
});

// ----- Interactions -----
client.on("interactionCreate", async (interaction) => {
  try {
    // Comando /painel
    if (interaction.isChatInputCommand() && interaction.commandName === "painel") {
      if (!isAdmin(interaction.member)) {
        return interaction.reply({ content: "❌ Apenas administradores podem usar.", ephemeral: true });
      }
      return interaction.reply({ embeds: [painelAdminEmbed()], components: [painelAdminRow()], ephemeral: true });
    }

    // Botões do painel de admin
    if (interaction.isButton() && interaction.customId.startsWith("painel_")) {
      if (!isAdmin(interaction.member)) {
        return interaction.reply({ content: "❌ Apenas administradores podem usar.", ephemeral: true });
      }

      if (interaction.customId === "painel_setarEntrega") {
        canalCorreioId = interaction.channelId;
      }
      if (interaction.customId === "painel_setarPainel") {
        canalPainelId = interaction.channelId;
        const canal = await client.channels.fetch(canalPainelId).catch(() => null);
        if (canal && canal.isTextBased()) {
          await canal.send({ embeds: [painelEmbed()], components: [escolhaRow()] });
        }
      }

      return interaction.update({ embeds: [painelAdminEmbed()], components: [painelAdminRow()] });
    }

    // Clique nos botões do painel público
    if (interaction.isButton() && (interaction.customId === "correio_anonimo" || interaction.customId === "correio_publico")) {
      const anonimo = interaction.customId === "correio_anonimo";

      const modal = new ModalBuilder()
        .setCustomId(`modal_${anonimo ? "anon" : "pub"}`)
        .setTitle("💌 Enviar Correio Elegante");

      const destinatario = new TextInputBuilder()
        .setCustomId("destinatario")
        .setLabel("Digite o @id da pessoa (ex: <@1234567890>)")
        .setStyle(TextInputStyle.Short)
        .setRequired(true);

      const mensagem = new TextInputBuilder()
        .setCustomId("mensagem")
        .setLabel("Escreva sua mensagem")
        .setStyle(TextInputStyle.Paragraph)
        .setMaxLength(1000)
        .setRequired(true);

      modal.addComponents(
        new ActionRowBuilder().addComponents(destinatario),
        new ActionRowBuilder().addComponents(mensagem)
      );

      await interaction.showModal(modal);
      return;
    }

    // Resposta do modal
    if (interaction.isModalSubmit() && (interaction.customId === "modal_anon" || interaction.customId === "modal_pub")) {
      const anonimo = interaction.customId === "modal_anon";
      const destinatario = interaction.fields.getTextInputValue("destinatario");
      const mensagem = interaction.fields.getTextInputValue("mensagem");

      const embed = new EmbedBuilder()
        .setTitle("💌 CORREIO ELEGANTE 💌")
        .setColor(0xff4dd2)
        .addFields(
          { name: "De:", value: anonimo ? "Anônimo 🤫" : `<@${interaction.user.id}>` },
          { name: "Para:", value: destinatario },
          { name: "Mensagem:", value: mensagem }
        )
        .setFooter({ text: `Enviado em ${new Date().toLocaleString()}` });

      let canal = canalCorreioId ? await client.channels.fetch(canalCorreioId).catch(() => null) : interaction.channel;

      if (!canal || !canal.isTextBased()) {
        return interaction.reply({ content: "⚠️ Canal de entrega inválido.", ephemeral: true });
      }

      await canal.send({ embeds: [embed] });
      enviadosTotal++;

      await interaction.reply({ content: "✅ Correio enviado com sucesso!", ephemeral: true });
    }
  } catch (err) {
    console.error("Erro:", err);
    if (interaction.isRepliable()) interaction.reply({ content: "❌ Ocorreu um erro.", ephemeral: true }).catch(() => {});
  }
});

client.login(TOKEN);
