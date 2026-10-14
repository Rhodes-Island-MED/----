import discord
from discord import app_commands
from discord.ext import commands

# 設定機器人的 Intention
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"機器人已上線：{bot.user.name} ({bot.user.id})")
    try:
        # 同步斜線指令 (Slash Commands) 到 Discord
        synced = await bot.tree.sync()
        print(f"成功同步 {len(synced)} 個斜線指令！")
    except Exception as e:
        print(f"同步指令時發生錯誤: {e}")

# 定義公告指令
@bot.tree.command(name="announce", description="發布預設排版的卡片公告")
@app_commands.describe(
    channel="選擇要發布公告的頻道",
    title="公告標題",
    content="公告內容 (可使用 \\n 換行)",
    ping_type="是否要 @Mention 標籤所有人或特定身份組",
    color="請輸入 Hex 顏色碼 (例如：#FF5733)"
)
@app_commands.choices(ping_type=[
    app_commands.Choice(name="不標籤", value="none"),
    app_commands.Choice(name="@everyone", value="everyone"),
    app_commands.Choice(name="@here", value="here")
])
# 限制只有擁有「管理訊息」權限的人才能使用此指令
@app_commands.default_permissions(manage_messages=True)
async def announce(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    title: str,
    content: str,
    ping_type: str = "none",
    color: str = "#3498db"
):
    # 轉換顏色字串為 Discord 支援的 Color
    try:
        hex_color = int(color.lstrip('#'), 16)
        embed_color = discord.Color(hex_color)
    except ValueError:
        embed_color = discord.Color.blue()

    # 建立 Embed 嵌入卡片
    embed = discord.Embed(
        title=title,
        description=content.replace("\\n", "\n"), # 支援輸入 \n 換行
        color=embed_color
    )
    # 設定頁尾顯示發布者資訊與時間
    embed.set_footer(
        text=f"發布者：{interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None
    )
    embed.timestamp = discord.utils.utcnow()

    # 處理 Mention
    mention_str = ""
    if ping_type == "everyone":
        mention_str = "@everyone"
    elif ping_type == "here":
        mention_str = "@here"

    try:
        # 發布到指定頻道
        await channel.send(content=mention_str if mention_str else None, embed=embed)
        # 回覆操作者（僅操作者自己看得見）
        await interaction.response.send_message(f"✅ 公告已成功發布至 {channel.mention}！", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"❌ 錯誤：機器人在 {channel.mention} 沒有發送訊息的權限！", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ 發布失敗：{e}", ephemeral=True)

# 啟動機器人
bot.run('MTU1OTg3NjY1MDIzMTkyNjkwNQ.GtTm4v.q9vjLqL08ePXZxtqy0nL6wAXT3PkMtRfFGTaC8')
