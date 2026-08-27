const { Client, GatewayIntentBits, SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, PermissionFlagsBits } = require('discord.js');
const fs = require('fs');
const path = require('path');

const client = new Client({
    intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages]
});

const TOKEN = process.env.GIVEAWAY_TOKEN || process.env.DISCORD_TOKEN;
const stockFilePath = path.join(__dirname, 'stock.json');

// دالة سحب حساب من الستوك
function getStock(category) {
    if (!fs.existsSync(stockFilePath)) return null;
    let data = JSON.parse(fs.readFileSync(stockFilePath, 'utf8'));
    if (!data[category] || data[category].length === 0) return null;
    const account = data[category].shift();
    fs.writeFileSync(stockFilePath, JSON.stringify(data, null, 4));
    return account;
}

client.once('ready', async () => {
    console.log(`✅ بوت الجيف أواي شغال بنجاح: ${client.user.tag}`);
    
    // تسجيل أوامر السلاش
    const commands = [
        new SlashCommandBuilder()
            .setName('giveaway')
            .setDescription('إنشاء جيف أواي جديد احترافي')
            .addStringOption(opt => opt.Name('prize').setDescription('الجوائز أو الحساب المراد توزيعه').setRequired(true))
            .addStringOption(opt => opt.Name('category').setDescription('نوع الحساب في الستوك (مثل: netflix, minecraft)').setRequired(true))
            .setDefaultMemberPermissions(PermissionFlagsBits.Administrator)
    ];

    await client.application.commands.set(commands);
});

client.on('interactionCreate', async interaction => {
    if (interaction.isChatInputCommand()) {
        if (interaction.commandName === 'giveaway') {
            const prize = interaction.options.getString('prize');
            const category = interaction.options.getString('category');

            const embed = new EmbedBuilder()
                .setTitle('🎉 **GIVEAWAY | جيف أواي جديد** 🎉')
                .setDescription(`جائزة مقدمة من: ${interaction.user}\n\n🎁 الجائزة: **${prize}**\n\nاضغط على الزر بالأسفل للمشاركة والدخول في السحب!`)
                .setColor(0x5865F2)
                .setTimestamp();

            const row = new ActionRowBuilder().addComponents(
                new ButtonBuilder()
                    .setCustomId(`join_gw_${category}`)
                    .setLabel('مشاركة 🎉')
                    .setStyle(ButtonStyle.Success)
            );

            await interaction.reply({ content: '✅ تم بدء الجيف أواي بنجاح!', ephemeral: true });
            await interaction.channel.send({ embeds: [embed], components: [row] });
        }
    } 
    
    else if (interaction.isButton()) {
        if (interaction.customId.startsWith('join_gw_')) {
            const category = interaction.customId.replace('join_gw_', '');
            const account = getStock(category);

            if (!account) {
                return interaction.reply({ content: '❌ عذراً، نفدت كمية الحسابات (Stock) حالياً!', ephemeral: true });
            }

            // إرسال الجائزة في الخاص مثل نظام نوفا
            try {
                await interaction.user.send(`🎉 **مبروك لقد فزت في الجيف أواي!**\n🎁 الحساب/الجوائز:\n\`\`\`${account}\`\`\``);
                await interaction.reply({ content: '🏆 مبروك! لقد فزت وتم إرسال تفاصيل الحساب على الخاص الخاص بك.', ephemeral: true });
            } catch (err) {
                await interaction.reply({ content: '⚠️ لقد فزت، ولكن يبدو أن رسائل الخاص (DM) مغلقة لديك! افتح الخاص واستمر.', ephemeral: true });
            }
        }
    }
});

client.login(TOKEN);
