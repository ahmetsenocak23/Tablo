import discord
from discord.ext import commands
from logic import DB_Manager
from config import DATABASE, Token
from discord import ui, ButtonStyle, TextStyle

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
manager = DB_Manager(DATABASE)


# Bot başlatıldığında terminale botun ismi ile hazır olduğuna dair bir mesaj gönderir
@bot.event
async def on_ready():
    print(f'Bot hazır! {bot.user} olarak giriş yapıldı.')

@bot.command(name='start')
async def start_command(ctx):
    await ctx.send("Merhaba! Ben bir proje yöneticisi botuyum.\nProjelerinizi ve onlara dair tüm bilgileri saklamanıza yardımcı olacağım! =)")
    await info(ctx)

@bot.command(name='info')
async def info(ctx):
    await ctx.send("""
Kullanabileceğiniz komutlar şunlardır:

!new_project - yeni bir proje eklemek
!projects - tüm projelerinizi listelemek
!update_projects - proje verilerini güncellemek
!skills - belirli bir projeye beceri eklemek
!delete - bir projeyi silmek

Ayrıca, proje adını yazarak projeyle ilgili tüm bilgilere göz atabilirsiniz!""")


# Yeni proje ekler 
@bot.command(name='new_project')
async def new_project(ctx):
    await ctx.send("Lütfen projenin adını girin!")

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
    # (wait for lar yanıt bekler)
    name = await bot.wait_for('message', check=check)
    data = [ctx.author.id, name.content]
    await ctx.send("Lütfen projeye ait bağlantıyı gönderin!")
    link = await bot.wait_for('message', check=check)
    data.append(link.content)

    statuses = [x[0] for x in manager.get_statuses()]
    await ctx.send("Lütfen projenin mevcut durumunu girin!", delete_after=60.0)
    await ctx.send("\n".join(statuses), delete_after=60.0)
    
    status = await bot.wait_for('message', check=check)
    if status.content not in statuses:
        await ctx.send("Seçtiğiniz durum listede bulunmuyor. Lütfen tekrar deneyin!", delete_after=60.0)
        return

    status_id = manager.get_status_id(status.content)
    data.append(status_id)
    manager.insert_project([tuple(data)])
    await ctx.send("Proje kaydedildi")


# Projects yazınca bazı sorular sorar ve
@bot.command(name='projects')
async def get_projects(ctx):
    user_id = ctx.author.id
    projects = manager.get_projects(user_id)
    if projects:
        # x ve ardından sayı tabloda kaçıncı sütün olduğunu belirtir
        text = "\n".join([f"Project name: {x[2]} \nLink: {x[4]}\n" for x in projects])
        await ctx.send(text)
    else:
        await ctx.send('Henüz herhangi bir projeniz yok!\nBir tane eklemeyi düşünün! !new_project komutunu kullanabilirsiniz.')

# Projenize beceri eklemenize olanak tanır
@bot.command(name='skills')
async def skills(ctx):
    user_id = ctx.author.id
    projects = manager.get_projects(user_id)
    if projects:
        projects = [x[2] for x in projects]
        await ctx.send('Bir beceri eklemek istediğiniz projeyi seçin')
        await ctx.send("\n".join(projects))

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        project_name = await bot.wait_for('message', check=check)
        if project_name.content not in projects:
            await ctx.send('Bu projeye sahip değilsiniz, lütfen tekrar deneyin! Beceri eklemek istediğiniz projeyi seçin')
            return

        skills = [x[1] for x in manager.get_skills()]
        await ctx.send('Bir beceri seçin')
        await ctx.send("\n".join(skills))

        skill = await bot.wait_for('message', check=check)
        if skill.content not in skills:
            await ctx.send('Görünüşe göre seçtiğiniz beceri listede yok! Lütfen tekrar deneyin! Bir beceri seçin')
            return

        manager.insert_skill(user_id, project_name.content, skill.content)
        await ctx.send(f'{skill.content} becerisi {project_name.content} projesine eklendi')
    else:
        await ctx.send('Henüz herhangi bir projeniz yok!\nBir tane eklemeyi düşünün! !new_project komutunu kullanabilirsiniz.')

@bot.command(name='delete')
async def delete_project(ctx):
    user_id = ctx.author.id
    projects = manager.get_projects(user_id)
    if projects:
        projects = [x[2] for x in projects]
        await ctx.send("Silmek istediğiniz projeyi seçin")
        
        # Alt satıra geçip projects ile birleştirir
        await ctx.send("\n".join(projects))

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        project_name = await bot.wait_for('message', check=check)
        if project_name.content not in projects:
            await ctx.send('Bu projeye sahip değilsiniz, lütfen tekrar deneyin!')
            return

        project_id = manager.get_project_id(project_name.content, user_id)
        manager.delete_project(user_id, project_id)
        await ctx.send(f'{project_name.content} projesi veri tabanından silindi!')
    else:
        await ctx.send('Henüz herhangi bir projeniz yok!\nBir tane eklemeyi düşünün! !new_project komutunu kullanabilirsiniz.')

@bot.command(name='update_projects')
async def update_projects(ctx):
    user_id = ctx.author.id
    projects = manager.get_projects(user_id)
    if projects:
        projects = [x[2] for x in projects]
        await ctx.send("Güncellemek istediğiniz projeyi seçin")
        await ctx.send("\n".join(projects))

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        # hata olup olmadığını kontrol eder.
        project_name = await bot.wait_for('message', check=check)
        if project_name.content not in projects:
            await ctx.send("Bir hata oldu! Lütfen güncellemek istediğiniz projeyi tekrar seçin:")
            return

        await ctx.send("Projede neyi değiştirmek istersiniz?")
        attributes = {'Proje adı': 'project_name', 'Açıklama': 'description', 'Proje bağlantısı': 'url', 'Proje durumu': 'status_id'}
        await ctx.send("\n".join(attributes.keys()))

        attribute = await bot.wait_for('message', check=check)
        if attribute.content not in attributes:
            await ctx.send("Hata oluştu! Lütfen tekrar deneyin!")
            return

        if attribute.content == 'Durum':
            statuses = manager.get_statuses()
            await ctx.send("Projeniz için yeni bir durum seçin")
            await ctx.send("\n".join([x[0] for x in statuses]))
            update_info = await bot.wait_for('message', check=check)
            if update_info.content not in [x[0] for x in statuses]:
                await ctx.send("Yanlış durum seçildi, lütfen tekrar deneyin!")
                return
            update_info = manager.get_status_id(update_info.content)
        else:
            await ctx.send(f"{attribute.content} için yeni bir değer girin")
            update_info = await bot.wait_for('message', check=check)
            update_info = update_info.content

        manager.update_projects(attributes[attribute.content], (update_info, project_name.content, user_id))
        await ctx.send("Tüm işlemler tamamlandı! Proje güncellendi!")
    else:
        await ctx.send('Henüz herhangi bir projeniz yok!\nBir tane eklemeyi düşünün! !new_project komutunu kullanabilirsiniz.')
class TestModal(ui.Modal, title='Test başlık'):
    # Modal pencerede metin alanları tanımlama
    field_1 = ui.TextInput(label='Kısa metin')
    field_2 = ui.TextInput(label='Uzun metin', style=TextStyle.paragraph)

    # Modal pencere istendiğinde çağrılan bir yöntem
    async def on_submit(self, interaction: discord.Interaction):
        # Girilen verilerle mesajı güncelleme
        await interaction.message.edit(content=f'Kısa metin: {self.field_1.value}\n'
                                               f'Uzun metin: {self.field_2.value}')
        # Yanıtın daha önce gönderilip gönderilmediğini kontrol etme
        if not interaction.response.is_done():
            # Gecikmeli yanıt için hazırlık yapma
            await interaction.response.defer()

# Buton tanımlama
class TestButton(ui.Button):
    # Belirli özellikler sahip bir butonun başlatılması
    def __init__(self, label="Test etiketi", style=ButtonStyle.blurple, row=0):
        super().__init__(label=label, style=style, row=row)

    # Butona basıldığında çağrılan bir yöntem
    async def callback(self, interaction: discord.Interaction):
        # Kullanıcıya doğrudan mesaj gönderme
        await interaction.user.send("Bir butona bastınız")
        # Butona basılan kanala bir mesaj gönderme
        await interaction.message.channel.send("Bir butona bastınız")
        # Modal pencereyi açma
        await interaction.response.send_modal(TestModal())
        # Basıldıktan sonra butonun stilini değiştirme
        self.style = ButtonStyle.gray

        # Yanıtın daha önce gönderilip gönderilmediğini kontrol etme
        if not interaction.response.is_done():
            # Gecikmeli yanıt için hazırlık yapma
            await interaction.response.defer()

# Buton içeren bir pencere (görünüm) nesnesi tanımlama
class TestView(ui.View):
    # Görünümü başlatma
    def __init__(self):
        super().__init__()
        # Görünüme bir buton ekleme
        self.add_item(TestButton(label="Test etiketi"))

# Bot yapılandırması
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Bot hazır olduğunda gönderilen bir olay
@bot.event
async def on_ready():
    # Başarılı yetkilendirme hakkında bir mesaj görüntüleme
    print(f'{bot.user} olarak giriş yapıldı')

# Butonu gösteren bir komut
@bot.command()
async def test(ctx):
    # Bir buton içeren görünüm ile mesaj gönderme
    await ctx.send("Aşağıdaki butona tıklayın:", view=TestView())

bot.run(Token)
