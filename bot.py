import os
import discord
from discord.ext import commands

# إعداد الصلاحيات
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="§", intents=intents)

# قائمة لحفظ الأيديوهات للأشخاص الذين أخذوا حساباً مسبقاً عبر الزر
claimed_users = set()

# حط الآيدي حقك هنا يا ملك عشان تستثنى من قيد الحساب الواحد وتجرب براحتك!
OWNER_ID = 1479080698009747519

@bot.event
async def on_ready():
    print(f"✅ تم تسجيل الدخول بنجاح كـ {bot.user}")
    await bot.change_presence(activity=discord.Game(name="§setup لوحة الحسابات | §sent للإرسال اليدوي"))

# --- 1. نظام الزر التفاعلي (Get Account) ---
class AccountView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="إيجاد حساب (Get Account)", style=discord.ButtonStyle.green, emoji="🎁", custom_id="get_account_btn")
    async def get_account_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        
        is_owner = (member.id == OWNER_ID)

        if not is_owner and member.id in claimed_users:
            await interaction.response.send_message("❌ **لقد قمت بالحصول على حساب مسبقاً! لا يمكنك أخذ حساب آخر لمنع الاحتكار.**", ephemeral=True)
            return

        try:
            with open("accounts.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            if not lines:
                await interaction.response.send_message("❌ عذراً، نفدت الحسابات من المخزون تماماً! ترقب التحديث القادم.", ephemeral=True)
                return

            account_line = lines[0].strip()
            
            if ":" in account_line:
                email, password = account_line.split(":", 1)
            else:
                email = account_line
                password = "غير محدد"

            is_low_stock = len(lines) <= 2

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

            with open("accounts.txt", "w", encoding="utf-8") as f:
                f.writelines(lines[1:])

            if not is_owner:
                claimed_users.add(member.id)
                await interaction.response.send_message(f"✅ **تم إرسال حساب جديد في الخاص يا {member.mention}! 🚀**", ephemeral=True)
            else:
                await interaction.response.send_message(f"👑 **أهلاً بك يا أونر! تم سحب الحساب وإرساله لخاصك بنجاح (بدون قيود). 🚀**", ephemeral=True)

        except FileNotFoundError:
            await interaction.response.send_message("❌ خطأ: ملف الحسابات `accounts.txt` غير موجود في مجلد البوت.", ephemeral=True)

# --- 2. أمر !setup لإرسال لوحة الزر ---
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

# --- 3. أمر §sent للإرسال اليدوي للفائزين بالجيف أواي ---
@bot.command(name="sent")
@commands.has_permissions(administrator=True)
async def manual_send(ctx, member: discord.Member):
    try:
        with open("accounts.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        if not lines:
            await ctx.send("❌ عذراً، نفدت الحسابات من المخزون (`accounts.txt`) تماماً!")
            return

        account_line = lines[0].strip()
        
        if ":" in account_line:
            email, password = account_line.split(":", 1)
        else:
            email = account_line
            password = "غير محدد"

        embed_acc = discord.Embed(
            title="🎁 مبروك فوزك بالجيف أواي! حساب ماينكرفت الخاص بك",
            description="إليك تفاصيل حسابك الجديد الذي تم إرساله لك يدوياً:",
            color=discord.Color.gold()
        )
        embed_acc.add_field(name="📧 البريد الإلكتروني (Email)", value=f"`{email}`", inline=False)
        embed_acc.add_field(name="🔑 كلمة المرور (Password)", value=f"`{password}`", inline=False)
        embed_acc.set_footer(text="MCFA Giveaway System")

        try:
            await member.send(embed=embed_acc)
        except discord.Forbidden:
            await ctx.send(f"❌ **عذراً يا {ctx.author.mention}، خاص العضو {member.mention} مغلق!** لم أتمكن من إرسال الحساب له.")
            return

        # حذف الحساب المرسل من الملف
        with open("accounts.txt", "w", encoding="utf-8") as f:
            f.writelines(lines[1:])

        await ctx.send(f"✅ **تم سحب حساب وإرساله بنجاح إلى الخاص لـ {member.mention}! 🎉**")
        
        try:
            await ctx.message.delete()
        except:
            pass

    except FileNotFoundError:
        await ctx.send("❌ خطأ: ملف الحسابات `accounts.txt` غير موجود في مجلد البوت.")

# تشغيل البوت
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN في متغيرات البيئة!")
