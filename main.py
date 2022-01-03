import pygame
import pygame_gui
from pytube import YouTube, Stream
from easygui import filesavebox, msgbox
import os
import pyffmpeg
from threading import Thread

pygame.init()

FFmpeg = pyffmpeg.FFmpeg()

pygame.display.set_caption("YouTube Downloader")
screen = pygame.display.set_mode((450, 130))
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 16)

# Render main program UI
MainUI = pygame.Surface(pygame.display.get_window_size())
MainUI.fill((30, 30, 30))
MainUI.fill((70, 70, 70), (0, 0, 450, 20))

text = font.render("YouTube Downloader", True, (255, 255, 255))
MainUI.blit(text, (450 / 2 - text.get_width() / 2, 0))

text = font.render("Put YouTube video URL here:", True, (100, 100, 100))
MainUI.blit(text, (20 + 300 / 2 - text.get_width() / 2, 20))

manager = pygame_gui.UIManager(pygame.display.get_window_size())
search_box = pygame_gui.elements.UITextEntryLine(pygame.Rect(20, 40, 300, 30), manager)
resolution_box = pygame_gui.elements.UIDropDownMenu(["360p", "480p", "720p", "1080p"], "360p", pygame.Rect(330, 42, 100, 22),
                                                    manager)

download_video = pygame_gui.elements.UIButton(pygame.Rect(60, 75, 150, 30), "Download Video", manager)
download_audio = pygame_gui.elements.UIButton(pygame.Rect(450 - 60 - 150, 75, 150, 30), "Download Audio", manager)

download_progressbar = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect(20, 110, 450 - 20 * 2, 10), manager)


def set_progress(prog: float):
    download_progressbar.health_percentage = prog
    download_progressbar.current_health = int(download_progressbar.health_percentage * 100)
    download_progressbar.rebuild()


set_progress(0)

time = 0
running = True
download_thread = 0
while running:
    delta_time = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.USEREVENT:
            # UI button was pressed
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                # check if there's something in search box
                if search_box.get_text():

                    def progress(stream, chunk, bytes_remaining):
                        global download_progressbar
                        stream: Stream
                        size = stream.filesize

                        set_progress(float(size - bytes_remaining) / float(size))


                    yt = YouTube(search_box.get_text())
                    yt.register_on_progress_callback(progress)

                    set_progress(0)

                    if yt:
                        if event.ui_element == download_video:
                            path = filesavebox(title="Specify output path", default="output.mp4")

                            def download():
                                try:
                                    yt.streams.filter(type="video", file_extension="mp4",
                                                      resolution=resolution_box.selected_option
                                                      if resolution_box.selected_option else None)[0]. \
                                        download(output_path=os.path.dirname(path), filename=os.path.split(path)[-1])
                                except Exception as e:
                                    msgbox(str(e),"Error occured")


                            download_thread = Thread(target=download)
                            download_thread.start()

                        elif event.ui_element == download_audio:
                            path = filesavebox(title="Specify output path", filetypes=["*.ogg", "*.mp3"])


                            def download():
                                yt.streams.filter(type="audio", file_extension="mp4")[0]. \
                                    download(output_path=os.path.dirname(path),
                                             filename=os.path.basename(path).split(".")[0] + ".mp4")
                                FFmpeg.convert(path[:-3] + "mp4", path)
                                os.remove(path[:-3] + "mp4")


                            download_thread = Thread(target=download)
                            download_thread.start()

        manager.process_events(event)

    time += 1
    manager.update(delta_time)

    screen.blit(MainUI, (0, 0))
    manager.draw_ui(screen)

    pygame.display.flip()
