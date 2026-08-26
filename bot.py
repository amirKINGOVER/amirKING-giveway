import discord
from discord.ext import commands

# إعداد الصلاحيات
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# قائمة لحفظ الأيديوهات للأشخاص الذين أخذوا حساباً مسبقاً
claimed_users = set()

# حط الآيدي حقك هنا يا ملك عشان تستثنى من قيد الحساب الواحد وتجرب براحتك!
OWNER_ID = 1479080698009747519

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح كـ {bot.user}")

# أمر !setup لإرسال لوحة التعليمات والزر الأخضر
@bot.command(name="setup")
@commands.has_permissions(administrator=True)
async def setup_panel(ctx):
    try:
        await ctx.message.delete()
    except:
        pass
    
    embed = discord.Embed(
        title="📖 تعليمات وكيفية استعمال نظام الحسابات",
        description=(
            "**أهلاً بك في نظام توزيع حسابات ماينكرفت المجانية!** 🎮\n\n"
            "**🔹 كيفية الاستعمال:**\n"
            "1️⃣ تأكد أن **رسائلك الخاصة (DM)** مفتوحة.\n"
            "2️⃣ اضغط على **الزر الأخضر** بالأسفل (`إيجاد حساب`).\n"
            "3️⃣ سيقوم البوت بسحب حساب جديد كلياً وإرساله لك في الخاص فوراً!\n\n"
            "⚠️ **ملاحظة هامة:**\n"
            "• لكل شخص حساب واحد فقط لضمان توزيع عادل للجميع."
        ),
        color=discord.Color.from_rgb(88, 101, 242)
    )
    embed.set_footer(text="MCFA Store System - نظام منع التكرار")
    
    view = AccountView()
    await ctx.send(embed=embed, view=view)

# تصميم الزر التفاعلي
class AccountView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="إيجاد حساب (Get Account)", style=discord.ButtonStyle.green, emoji="🎁", custom_id="get_account_btn")
    async def get_account_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        
        # 1. التحقق مما إذا كان المستخدم هو الأنر (استثناء من القيد)
        is_owner = (member.id == OWNER_ID)

        # إذا لم يكن هو الأنر، نتحقق مما إذا كان قد أخذ حساباً من قبل
        if not is_owner and member.id in claimed_users:
            await interaction.response.send_message("❌ **لقد قمت بالحصول على حساب مسبقاً! لا يمكنك أخذ حساب آخر لمنع الاحتكار.**", ephemeral=True)
            return

        try:
            with open("accounts.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            if not lines:
                await interaction.response.send_message("❌ عذراً، نفدت الحسابات من المخزون تماماً! ترقب التحديث القادم.", ephemeral=True)
                return

            # قراءة أول حساب وتنظيفه من الفراغات
            account_line = lines[0].strip()
            
            if ":" in account_line:
                email, password = account_line.split(":", 1)
            else:
                email = account_line
                password = "غير محدد"

            is_low_stock = len(lines) <= 2

            # إنشاء تصميم الحساب لإرساله بالخاص
            embed_acc = discord.Embed(
                title="🎮 مبروك! حساب ماينكرفت الخاص بك",
                description="إليك تفاصيل حسابك الجديد الذي تم سحبه خصيصاً لك:",
                color=discord.Color.green()
            )
            embed_acc.add_field(name="📧 البريد الإلكتروني (Email)", value=f"`{email}`", inline=False)
            embed_acc.add_field(name="🔑 كلمة المرور (Password)", value=f"`{password}`", inline=False)

            if is_low_stock:
                embed_acc.add_field(
                    name="⚠️ تنبيه هام (قلة الحسابات)", 
                    value="*نظراً لقلة الحسابات المتبقية في المخزون، هذا الحساب قد يكون قديماً أو مستخدماً من قبل شخص آخر.*", 
                    inline=False
                )

            embed_acc.set_footer(text="شكراً لاستخدامك سيرفرنا!")

            try:
                await member.send(embed=embed_acc)
            except discord.Forbidden:
                await interaction.response.send_message("❌ **خاصك مغلق!** يرجى فتح الخاص (Direct Messages) لتتمكن من استلام الحساب.", ephemeral=True)
                return

            # حذف الحساب من الملف
            with open("accounts.txt", "w", encoding="utf-8") as f:
                f.writelines(lines[1:])

            # إذا لم يكن أنر، نسجله في القائمة حتى لا يأخذ حساباً ثانياً
            if not is_owner:
                claimed_users.add(member.id)
                await interaction.response.send_message(f"✅ **تم إرسال حساب جديد في الخاص يا {member.mention}! 🚀**", ephemeral=True)
            else:
                # رسالة خاصة للأنر تفيد بأنه سحب حساباً بصلاحيات المالك
                await interaction.response.send_message(f"👑 **أهلاً بك يا أونر! تم سحب الحساب وإرساله لخاصك بنجاح (بدون قيود). 🚀**", ephemeral=True)

        except FileNotFoundError:
            await interaction.response.send_message("❌ خطأ: ملف الحسابات `accounts.txt` غير موجود في مجلد البوت.", ephemeral=True)

# تشغيل البوت
client.login(process.env.DISCORD_TOKEN);