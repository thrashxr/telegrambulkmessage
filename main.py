#!/usr/bin/env python3

import asyncio
import sys
import signal
from typing import Optional

import config
from session_manager import SessionManager
from group_manager import GroupManager
from message_sender import MessageSender

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn

console = Console()


class TelegramBulkSender:
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.group_manager: Optional[GroupManager] = None
        self.message_sender: Optional[MessageSender] = None
        self.selected_groups: list[dict] = []
    
    def print_header(self):
        console.print(Panel.fit(
            "[bold blue]TELEGRAM BULK MESSAGE SENDER[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        ))
    
    def print_menu(self):
        table = Table(title="ANA MENÜ", show_header=False, box=None)
        table.add_column("Seçenek", style="cyan")
        table.add_column("Açıklama")
        
        table.add_row("1", "👤 Hesap Yönetimi")
        table.add_row("2", "👥 Grup Yönetimi")
        table.add_row("3", "📤 Mesaj Gönder")
        table.add_row("4", "⚙️  Ayarlar")
        table.add_row("0", "🚪 Çıkış")
        
        console.print(Panel(table, title="[bold]Menü[/bold]", border_style="green"))
    
    def print_account_menu(self):
        table = Table(show_header=False, box=None)
        table.add_column("Seçenek", style="cyan")
        table.add_column("Açıklama")
        
        table.add_row("1", "➕ Yeni Hesap Ekle")
        table.add_row("2", "📂 Kayıtlı Hesap Yükle")
        table.add_row("3", "📋 Kayıtlı Hesapları Listele")
        table.add_row("4", "🗑️  Hesap Sil")
        table.add_row("0", "⬅️  Geri")
        
        console.print(Panel(table, title="[bold]Hesap Yönetimi[/bold]", border_style="blue"))
    
    def print_group_menu(self):
        table = Table(show_header=False, box=None)
        table.add_column("Seçenek", style="cyan")
        table.add_column("Açıklama")
        
        table.add_row("1", "📋 Grupları Listele")
        table.add_row("2", "➕ Gruba Katıl")
        table.add_row("3", "✅ Hedef Grupları Seç")
        table.add_row("4", "📋 Seçili Grupları Göster")
        table.add_row("0", "⬅️  Geri")
        
        console.print(Panel(table, title="[bold]Grup Yönetimi[/bold]", border_style="magenta"))
    
    def print_message_menu(self):
        table = Table(show_header=False, box=None)
        table.add_column("Seçenek", style="cyan")
        table.add_column("Açıklama")
        
        table.add_row("1", "📝 Tek Seferlik Gönder")
        table.add_row("2", "🔄 Döngü Modunda Gönder")
        table.add_row("3", "🖼️  Resimli Mesaj Gönder")
        table.add_row("0", "⬅️  Geri")
        
        console.print(Panel(table, title="[bold]Mesaj Gönder[/bold]", border_style="yellow"))
    
    def print_settings_menu(self):
        settings_text = ""
        if self.message_sender:
            settings_text = (
                f"[dim]Grup arası bekleme: {self.message_sender.group_delay} sn[/dim]\n"
                f"[dim]Döngü arası bekleme: {self.message_sender.loop_delay} sn[/dim]\n\n"
            )
        
        table = Table(show_header=False, box=None)
        table.add_column("Seçenek", style="cyan")
        table.add_column("Açıklama")
        
        table.add_row("1", "⏱️  Grup Arası Bekleme Süresi")
        table.add_row("2", "🔄 Döngü Arası Bekleme Süresi")
        table.add_row("0", "⬅️  Geri")
        
        console.print(Panel(settings_text + "Ayarlar:", title="[bold]Ayarlar[/bold]", border_style="white"))
        console.print(table)
    
    async def check_credentials(self) -> bool:
        if not config.validate_credentials():
            console.print("[bold red]❌ HATA: API bilgileri yapılandırılmamış![/bold red]")
            console.print(Panel(
                "1. https://my.telegram.org adresine gidin\n"
                "2. API Development Tools bölümünden API_ID ve API_HASH alın\n"
                "3. .env.example dosyasını .env olarak kopyalayın\n"
                "4. .env dosyasına API bilgilerinizi girin",
                title="Yapılması Gerekenler", border_style="red"
            ))
            return False
        return True
    
    async def check_login(self) -> bool:
        if not self.session_manager.get_active_client():
            console.print("[bold yellow]⚠️  Önce bir hesaba giriş yapmalısınız![/bold yellow]")
            return False
        return True
    
    async def handle_account_menu(self):
        while True:
            self.print_account_menu()
            choice = Prompt.ask("Seçim", choices=["1", "2", "3", "4", "0"])
            
            if choice == "1":
                phone = Prompt.ask("📱 Telefon numarası (+90...)")
                if phone:
                    with console.status("[bold green]Giriş yapılıyor..."):
                        success, msg = await self.session_manager.login(phone)
                    if success:
                        console.print(f"[bold green]✅ {msg}[/bold green]")
                        self._init_managers()
                    else:
                        console.print(f"[bold red]❌ {msg}[/bold red]")
            
            elif choice == "2":
                sessions = self.session_manager.list_saved_sessions()
                if not sessions:
                    console.print("[yellow]📭 Kayıtlı hesap bulunamadı.[/yellow]")
                    continue
                
                table = Table(title="Kayıtlı Hesaplar")
                table.add_column("No", style="cyan")
                table.add_column("Hesap", style="green")
                
                for i, session in enumerate(sessions, 1):
                    table.add_row(str(i), session)
                console.print(table)
                
                idx = IntPrompt.ask("Hesap seçin (numara)", default=0) - 1
                if 0 <= idx < len(sessions):
                    with console.status("[bold green]Hesap yükleniyor..."):
                        success, msg = await self.session_manager.load_session(sessions[idx])
                    if success:
                        console.print(f"[bold green]✅ {msg}[/bold green]")
                        self._init_managers()
                    else:
                        console.print(f"[bold red]❌ {msg}[/bold red]")
                else:
                    console.print("[red]❌ Geçersiz seçim.[/red]")
            
            elif choice == "3":
                sessions = self.session_manager.list_saved_sessions()
                if sessions:
                    table = Table(title="Kayıtlı Hesaplar")
                    table.add_column("No", style="cyan")
                    table.add_column("Hesap", style="green")
                    table.add_column("Durum", style="yellow")
                    
                    for i, session in enumerate(sessions, 1):
                        active = "Aktif" if session == self.session_manager.get_active_phone() else ""
                        table.add_row(str(i), session, active)
                    console.print(table)
                else:
                    console.print("[yellow]📭 Kayıtlı hesap bulunamadı.[/yellow]")
            
            elif choice == "4":
                sessions = self.session_manager.list_saved_sessions()
                if not sessions:
                    console.print("[yellow]📭 Silinecek hesap bulunamadı.[/yellow]")
                    continue
                
                table = Table(title="Silinecek Hesap")
                table.add_column("No", style="cyan")
                table.add_column("Hesap", style="red")
                
                for i, session in enumerate(sessions, 1):
                    table.add_row(str(i), session)
                console.print(table)
                
                idx = IntPrompt.ask("Hesap seçin (numara)", default=0) - 1
                if 0 <= idx < len(sessions):
                    if Confirm.ask(f"[bold red]{sessions[idx]} hesabını silmek istediğinize emin misiniz?[/bold red]"):
                        success, msg = await self.session_manager.logout(sessions[idx])
                        if success:
                            console.print(f"[bold green]✅ {msg}[/bold green]")
                        else:
                            console.print(f"[bold red]❌ {msg}[/bold red]")
                else:
                    console.print("[red]❌ Geçersiz seçim.[/red]")
            
            elif choice == "0":
                break
    
    def _init_managers(self):
        client = self.session_manager.get_active_client()
        if client:
            self.group_manager = GroupManager(client)
            self.message_sender = MessageSender(client)
    
    async def handle_group_menu(self):
        if not await self.check_login():
            return
        
        while True:
            self.print_group_menu()
            choice = Prompt.ask("Seçim", choices=["1", "2", "3", "4", "0"])
            
            if choice == "1":
                with console.status("[bold green]Gruplar yükleniyor..."):
                    groups = await self.group_manager.fetch_groups()
                
                if groups:
                    table = Table(title=f"Gruplarınız ({len(groups)} adet)")
                    table.add_column("No", style="cyan")
                    table.add_column("Tip", style="magenta")
                    table.add_column("Başlık", style="green")
                    table.add_column("Üye Sayısı", style="yellow")
                    
                    for i, g in enumerate(groups, 1):
                        members = str(g['members']) if g['members'] else "-"
                        table.add_row(str(i), g['type'], g['title'], members)
                    console.print(table)
                else:
                    console.print("[yellow]📭 Hiç grup bulunamadı.[/yellow]")
            
            elif choice == "2":
                link = Prompt.ask("🔗 Grup linki veya username")
                if link:
                    with console.status("[bold green]Gruba katılınıyor..."):
                        success, msg = await self.group_manager.join_group(link)
                    if success:
                        console.print(f"[bold green]✅ {msg}[/bold green]")
                    else:
                        console.print(f"[bold red]❌ {msg}[/bold red]")
            
            elif choice == "3":
                groups = self.group_manager.list_groups()
                if not groups:
                    console.print("[yellow]⚠️  Önce grupları listeleyin (seçenek 1).[/yellow]")
                    continue
                
                table = Table(title="Gruplar")
                table.add_column("Seçili", style="bold green")
                table.add_column("No", style="cyan")
                table.add_column("Başlık")
                
                for i, g in enumerate(groups, 1):
                    selected = "[green]✓[/green]" if g in self.selected_groups else " "
                    table.add_row(selected, str(i), g['title'])
                console.print(table)
                
                console.print("[dim]Birden fazla grup seçmek için virgülle ayırın (örn: 1,3,5)[/dim]")
                console.print("[dim]'all' yazarak tümünü seçebilirsiniz[/dim]")
                console.print("[dim]'clear' yazarak seçimi temizleyebilirsiniz[/dim]")
                
                selection = Prompt.ask("Seçim").lower()
                
                if selection == "all":
                    self.selected_groups = groups.copy()
                    console.print(f"[bold green]✅ {len(groups)} grup seçildi.[/bold green]")
                elif selection == "clear":
                    self.selected_groups = []
                    console.print("[bold green]✅ Seçim temizlendi.[/bold green]")
                else:
                    try:
                        indices = [int(x.strip()) - 1 for x in selection.split(",")]
                        self.selected_groups = []
                        for idx in indices:
                            if 0 <= idx < len(groups):
                                self.selected_groups.append(groups[idx])
                        console.print(f"[bold green]✅ {len(self.selected_groups)} grup seçildi.[/bold green]")
                    except ValueError:
                        console.print("[red]❌ Geçersiz format.[/red]")
            
            elif choice == "4":
                if self.selected_groups:
                    table = Table(title=f"Seçili Gruplar ({len(self.selected_groups)} adet)")
                    table.add_column("No", style="cyan")
                    table.add_column("Başlık", style="green")
                    
                    for i, g in enumerate(self.selected_groups, 1):
                        table.add_row(str(i), g['title'])
                    console.print(table)
                else:
                     console.print("[yellow]📭 Henüz grup seçilmedi.[/yellow]")
            
            elif choice == "0":
                break
    
    async def handle_message_menu(self):
        if not await self.check_login():
            return
        
        if not self.selected_groups:
            console.print("[bold yellow]⚠️  Önce hedef grupları seçmelisiniz![/bold yellow]")
            console.print("   Grup Yönetimi > Hedef Grupları Seç")
            return
        
        while True:
            self.print_message_menu()
            console.print(f"[dim]📊 Seçili grup: {len(self.selected_groups)} adet[/dim]")
            choice = Prompt.ask("Seçim", choices=["1", "2", "3", "0"])
            
            if choice == "1":
                await self._send_messages(loop=False, with_image=False)
            
            elif choice == "2":
                await self._send_messages(loop=True, with_image=False)
            
            elif choice == "3":
                await self._send_messages(loop=False, with_image=True)
            
            elif choice == "0":
                break
    
    async def _send_messages(self, loop: bool = False, with_image: bool = False):
        message = Prompt.ask("\n📝 Mesajınızı girin (Premium emoji desteklenir)")
        
        if not message:
            console.print("[red]❌ Mesaj boş olamaz.[/red]")
            return
        
        image_path = None
        if with_image:
            image_path = Prompt.ask("\n🖼️  Resim yolu (örn: /path/to/image.jpg)")
            if not image_path:
                console.print("[yellow]⚠️  Resim yolu belirtilmedi, sadece metin gönderilecek.[/yellow]")
                image_path = None
        
        if loop:
            console.print("[bold yellow]🔄 Döngü modu aktif. Durdurmak için Ctrl+C kullanın.[/bold yellow]")
            console.print(f"   Grup arası bekleme: {self.message_sender.group_delay} sn")
            console.print(f"   Döngü arası bekleme: {self.message_sender.loop_delay} sn")
        
        if not Confirm.ask("\n▶️  Gönderimi başlatmak istiyor musunuz?"):
            console.print("[red]❌ Gönderim iptal edildi.[/red]")
            return
        
        console.print(Panel("📤 GÖNDERIM BAŞLIYOR", style="bold green"))
        
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
        )
        
        try:
            with progress:
                task_id = progress.add_task("[cyan]Mesajlar gönderiliyor...", total=len(self.selected_groups))
                
                def progress_callback(title, success, msg):
                    if success:
                        console.print(f"[green]✓ {title}[/green]")
                    else:
                        console.print(f"[red]✗ {title}: {msg}[/red]")
                    progress.advance(task_id)

                results = await self.message_sender.send_to_groups(
                    self.selected_groups,
                    message,
                    image_path,
                    loop=loop,
                    callback=progress_callback
                )
            
            table = Table(title="Sonuçlar", show_header=True)
            table.add_column("Durum", style="bold")
            table.add_column("Sayı")
            
            table.add_row("✅ Başarılı", str(results['success']), style="green")
            table.add_row("❌ Başarısız", str(results['failed']), style="red")
            table.add_row("📊 Toplam", str(results['total']), style="blue")
            if loop:
                table.add_row("🔄 Döngü sayısı", str(results['loop_count']), style="yellow")
            
            console.print(table)
            
        except KeyboardInterrupt:
            self.message_sender.stop()
            console.print("\n\n[bold red]⚠️  Gönderim kullanıcı tarafından durduruldu.[/bold red]")
    
    async def handle_settings_menu(self):
        if not self.message_sender:
            print("\n⚠️  Önce bir hesaba giriş yapmalısınız!")
            return
        
        while True:
            self.print_settings_menu()
            choice = Prompt.ask("Seçim", choices=["1", "2", "0"])
            
            if choice == "1":
                delay = IntPrompt.ask("⏱️  Grup arası bekleme süresi (saniye)")
                if delay >= 0:
                    self.message_sender.set_delays(group_delay=delay)
                    console.print(f"[bold green]✅ Grup arası bekleme: {delay} saniye olarak ayarlandı.[/bold green]")
                else:
                    console.print("[red]❌ Süre 0 veya daha büyük olmalı.[/red]")
            
            elif choice == "2":
                delay = IntPrompt.ask("🔄 Döngü arası bekleme süresi (saniye)")
                if delay >= 0:
                    self.message_sender.set_delays(loop_delay=delay)
                    console.print(f"[bold green]✅ Döngü arası bekleme: {delay} saniye olarak ayarlandı.[/bold green]")
                else:
                    console.print("[red]❌ Süre 0 veya daha büyük olmalı.[/red]")
            
            elif choice == "0":
                break
    
    async def run(self):
        if not await self.check_credentials():
            return
        
        self.print_header()
        
        active = self.session_manager.get_active_phone()
        if active:
            console.print(f"[bold green]👤 Aktif hesap: {active}[/bold green]")
        else:
             console.print("[dim]👤 Aktif hesap: Yok[/dim]")
        
        try:
            while True:
                self.print_menu()
                
                active = self.session_manager.get_active_phone()
                if active:
                    console.print(f"[bold green]👤 Aktif: {active}[/bold green]")
                
                choice = Prompt.ask("Seçim", choices=["1", "2", "3", "4", "0"])
                
                if choice == "1":
                    await self.handle_account_menu()
                elif choice == "2":
                    await self.handle_group_menu()
                elif choice == "3":
                    await self.handle_message_menu()
                elif choice == "4":
                    await self.handle_settings_menu()
                elif choice == "0":
                    break
        
        finally:
            console.print("[bold blue]👋 Çıkış yapılıyor...[/bold blue]")
            await self.session_manager.disconnect_all()
            console.print("[bold green]✅ Güle güle![/bold green]")


def main():
    app = TelegramBulkSender()
    
    def signal_handler(sig, frame):
        console.print("\n\n[bold red]⚠️  Program sonlandırılıyor...[/bold red]")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    asyncio.run(app.run())


if __name__ == "__main__":
    main()
