const { Client, GatewayIntentBits, REST, Routes, SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');
const fs = require('fs');

const client = new Client({
    intents: [GatewayIntentBits.Guilds]
});

// قراءة الـ Token من متغيرات البيئة في ريلواي
const TOKEN = process.env.GIVEAWAY_TOKEN || process.env.DISCORD_TOKEN;

// تعريف أمر /giveaway
const commands = [
    new SlashCommandBuilder()
        .setName('giveaway')
        .setDescription('إنشاء جيف أواي لتوزيع الحسابات (زي نوفا)')
        .addStringOption(option =>
            option.setName('prize')
                .setDescription('اسم الجائزة (مثلاً: Minecraft Account)')
                .setRequired(true))
        .addStringOption(option =>
            option.setName('category')
                .setDescription('اسم الفئة في ملف الستوك (مثلاً: minecraft)')
                .setRequired(true))
].map(command => command.toJSON());

client.once('ready', async () => {
    console.log(`✅ البوت اشتغل بنجاح باسم: ${client.user.tag}`);

    // تسجيل الأوامر تلقائياً أول ما يشتغل البوت
    const rest = new REST({ version: '10' }).setToken(TOKEN);
    try {
        console.log('🔄 جاري تسجيل أوامر السلاش...');
        await rest.put(
            Routes.applicationCommands(client.user.id),
            { body: commands },
        );
        console.log('✨ تم تسجيل الأوامر بنجاح في ديسكورد!');
    } catch (error) {
        console.error('❌ خطأ أثناء تسجيل الأوامر:', error);
    }
});

client.on('interactionCreate', async interaction => {
    // 1. التعامل مع أمر /giveaway
    if (interaction.isChatInputCommand() && interaction.commandName === 'giveaway') {
        const prize = interaction.options.getString('prize');
        const category = interaction.options.getString('category');

        const embed = new EmbedBuilder()
            .setTitle('🎉 جيف أواي جديد لتوزيع الحسابات')
            .setDescription(`**الجائزة:** ${prize}\n**الفئة:** ${category}\n\nاضغط على الزر بالأسفل للمشاركة والحصول على حسابك فوراً!`)
            .setColor('#5865F2')
            .setTimestamp();

        const row = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId(`claim_${category}`)
                    .setLabel('مشاركة 🎉')
                    .setStyle(ButtonStyle.Success),
            );

        await interaction.reply({ embeds: [embed], components: [row] });
    }

    // 2. التعامل مع الضغط على زر المشاركة وسحب الحساب
    if (interaction.isButton() && interaction.customId.startsWith('claim_')) {
        const category = interaction.customId.replace('claim_', '');

        try {
            // قراءة ملف الستوك
            if (!fs.existsSync('./stock.json')) {
                return interaction.reply({ content: '❌ ملف `stock.json` غير موجود!', ephemeral: true });
            }

            const rawData = fs.readFileSync('./stock.json');
            let stockData = JSON.parse(rawData);

            // التحقق من وجود الفئة وأن فيها حسابات
            if (!stockData[category] || stockData[category].length === 0) {
                return interaction.reply({ content: `❌ عذراً، نفدت حسابات فئة **${category}** حالياً!`, ephemeral: true });
            }

            // سحب أول حساب من القائمة
            const account = stockData[category].shift();

            // حفظ التحديثات في الملف (حذف الحساب المستخدم لضمان عدم تكراره)
            fs.writeFileSync('./stock.json', JSON.stringify(stockData, null, 4));

            // إرسال الحساب للمستخدم على الخاص (DM)
            await interaction.user.send(`🎁 **مبروك فوزك بالجائزة!**\nبيانات الحساب الخاص بك:\n\`\`\`${account}\`\`\``);

            await interaction.reply({ content: '✅ تم إرسال الحساب إلى رسائلك الخاصة (DM)! تحقق من الخاص.', ephemeral: true });

        } catch (error) {
            console.error('❌ خطأ أثناء توزيع الحساب:', error);
            await interaction.reply({ content: '❌ حدث خطأ أثناء محاولة تسليم الحساب، يرجى مراجعة المشرف.', ephemeral: true });
        }
    }
});

client.login(TOKEN);
