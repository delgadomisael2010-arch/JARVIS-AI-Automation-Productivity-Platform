import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import threading
import time
import psutil
import requests
import core.servidor_biometria as servidor_biometria
import customtkinter as ctk
from tkinter import Canvas
import math
import random
from core.ouvir import ouvir_mic
import core.ouvir as ouvir
from core.cerebro import pensar
from core.falar import jarvis_falar


COR_FUNDO = "#000508"
COR_PRIMARIA = "#00E5FF"
COR_SECUNDARIA = "#0099DD"
COR_ALERTA = "#FF3366"
COR_OURO = "#FFD700"
COR_VERDE = "#00FF99"
COR_TEXTO_DIM = "#0A4A6E"
COR_PAINEL = "#050A12"
COR_BORDA = "#006688"
COR_GLOW = "#00DDFF"
COR_PROFESSOR = "#FFD700"
COR_PROFESSOR_DIM = "#8B6914"
COR_PROFESSOR_GLOW = "#FFF0A0"

FONTE_TITULO = ("Bahnschrift", 28, "bold")
FONTE_HUD = ("Consolas", 13, "bold")
FONTE_PEQUENA = ("Consolas", 11)
FONTE_CHAT = ("Consolas", 12)
FONTE_BOTAO = ("Consolas", 13, "bold")


NIVEL_ACESSO_ATUAL = 1
NIVEL_PRE_SELECIONADO = 1

PROTOCOLOS_ACESSO = {
    6: ("PROTOCOLO PROFESSORA", "TEACHER",  "#FF00FF"),
    5: ("PROTOCOLO OMNIPOTENTE","ADMIN",    "#00E5FF"),
    4: ("PROTOCOLO OPERACIONAL","OPERATOR", "#00FF99"),
    3: ("PROTOCOLO ANALÍTICO",  "ANALYST",  "#FFD700"),
    2: ("PROTOCOLO LIMITADO",   "GUEST",    "#0099DD"),
    1: ("ACESSO RESTRITO",      "BLOQUEADO","#FF3366"),
}

COMANDOS_RESTRITOS = {
    "eliminar": 5,
    "formatar": 5,
    "reiniciar": 4,
    "sistema":  3,
    "acesso":   3,
    "ficheiro": 2,
}

def definir_status_seguranca(nivel):
    return PROTOCOLOS_ACESSO.get(nivel, ("DESCONHECIDO", "???", "#FFFFFF"))

def nivel_pode_executar(texto, nivel):
    for palavra, minimo in COMANDOS_RESTRITOS.items():
        if palavra in texto.lower() and nivel < minimo:
            return False, minimo
    return True, 0

def obter_telemetria():
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        try:
            clima_req = requests.get("https://wttr.in/Lisboa?format=%t+%C", timeout=2)
            clima = clima_req.text.strip() if clima_req.status_code == 200 else "Offline"
        except Exception:
            clima = "Erro de Conexão"
    except Exception:
        cpu, ram, clima = 0, 0, "Erro de Sistema"
    return cpu, ram, clima


class ArcReactorUltra(Canvas):
    def __init__(self, parent, size=140, **kwargs):
        super().__init__(parent, width=size, height=size,
                         bg=COR_FUNDO, highlightthickness=0, **kwargs)
        self.size = size
        self.cx = size // 2
        self.cy = size // 2
        self.angle = 0
        self.pulse = 0
        self._draw()

    def _draw(self):
        self.delete("all")
        cx, cy, s = self.cx, self.cy, self.size
        p = 0.5 + 0.5 * math.sin(self.pulse * 0.05)

        r_outer = s * 0.48
        for layer in range(12, 0, -1):
            alpha_r = r_outer + layer * 1.5
            fade = int(25 + (12 - layer) * 3 + p * 20)
            fade = min(fade, 255)
            glow_col = f"#00{fade:02x}{min(fade + 30, 255):02x}"
            self.create_oval(cx - alpha_r, cy - alpha_r,
                             cx + alpha_r, cy + alpha_r,
                             outline=glow_col, width=1)

        self.create_oval(cx - r_outer, cy - r_outer,
                         cx + r_outer, cy + r_outer,
                         outline=COR_GLOW, width=3)

        for i in range(12):
            a_start = self.angle + i * 30
            brightness = 1.0 if i % 3 == 0 else 0.4
            seg_b = int(255 * brightness)
            seg_col = f"#00{seg_b:02x}{seg_b:02x}"
            self.create_arc(cx - r_outer + 5, cy - r_outer + 5,
                            cx + r_outer - 5, cy + r_outer - 5,
                            start=a_start, extent=18,
                            outline=seg_col, style="arc", width=3)

        r_mid = s * 0.34
        mid_r = min(int(180 + p * 40), 255)
        mid_col = f"#00{mid_r:02x}ff"
        self.create_oval(cx - r_mid, cy - r_mid,
                         cx + r_mid, cy + r_mid,
                         outline=mid_col, width=2)

        for i in range(8):
            a = -self.angle * 1.8 + i * 45
            x1 = cx + r_mid * math.cos(math.radians(a))
            y1 = cy + r_mid * math.sin(math.radians(a))
            x2 = cx + (r_mid - 10) * math.cos(math.radians(a))
            y2 = cy + (r_mid - 10) * math.sin(math.radians(a))
            self.create_line(x1, y1, x2, y2, fill=mid_col, width=2)

        r_hex = s * 0.18
        pts = []
        for i in range(6):
            a = math.radians(60 * i + self.angle * 0.7)
            pts += [cx + r_hex * math.cos(a), cy + r_hex * math.sin(a)]
        hex_b = min(int(200 + p * 55), 255)
        hex_col = f"#00{hex_b:02x}ff"
        self.create_polygon(pts, outline=hex_col, fill=COR_PAINEL, width=2)

        r_tri = s * 0.12
        for i in range(3):
            a = math.radians(120 * i - self.angle * 0.5)
            x = cx + r_tri * math.cos(a)
            y = cy + r_tri * math.sin(a)
            self.create_oval(x - 3, y - 3, x + 3, y + 3,
                             fill=COR_PRIMARIA, outline="white", width=1)

        r_core = s * 0.08
        core_g = min(int(220 + p * 35), 255)
        core_col = f"#00{core_g:02x}ff"
        for i in range(3, 0, -1):
            cr = r_core + i * 2
            ca = max(int(50 - i * 15), 0)
            ca2 = min(ca + 20, 255)
            self.create_oval(cx - cr, cy - cr, cx + cr, cy + cr,
                             fill=f"#00{ca:02x}{ca2:02x}", outline="")
        self.create_oval(cx - r_core, cy - r_core,
                         cx + r_core, cy + r_core,
                         fill=core_col, outline="white", width=2)

        self.angle = (self.angle + 2.5) % 360
        self.pulse += 1
        self.after(35, self._draw)


class HudLineChart(Canvas):
    def __init__(self, parent, label="", width=340, height=60, color=COR_PRIMARIA, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=COR_PAINEL, highlightthickness=1,
                         highlightbackground=COR_BORDA, **kwargs)
        self.w = width
        self.h = height
        self.label = label
        self.color = color
        self.history = [0] * 40
        self._render()

    def update_value(self, v):
        self.history.append(max(0, min(100, v)))
        if len(self.history) > 40:
            self.history.pop(0)
        self._render()

    def _render(self):
        self.delete("all")
        for i in range(1, 4):
            y = int(self.h * i / 4)
            self.create_line(0, y, self.w, y, fill=COR_TEXTO_DIM, width=1)

        pts = []
        n = len(self.history)
        for i, v in enumerate(self.history):
            x = int(i * self.w / (n - 1)) if n > 1 else 0
            y = int(self.h - (v / 100) * (self.h - 4) - 2)
            pts.append((x, y))

        if len(pts) >= 2:
            poly_pts = [(pts[0][0], self.h)] + pts + [(pts[-1][0], self.h)]
            flat = [coord for p in poly_pts for coord in p]
            self.create_polygon(flat, fill=COR_TEXTO_DIM, outline="")
            for i in range(len(pts) - 1):
                self.create_line(pts[i][0], pts[i][1],
                                 pts[i+1][0], pts[i+1][1],
                                 fill=self.color, width=2)
            lx, ly = pts[-1]
            self.create_oval(lx - 3, ly - 3, lx + 3, ly + 3,
                             fill=self.color, outline="white", width=1)

        val = self.history[-1] if self.history else 0
        self.create_text(6, 8, text=self.label, anchor="nw",
                         fill=self.color, font=("Consolas", 9, "bold"))
        self.create_text(self.w - 6, 8, text=f"{val:.0f}%", anchor="ne",
                         fill="white", font=("Consolas", 9, "bold"))


class HudBarPremium(Canvas):
    def __init__(self, parent, label="", width=240, color=COR_PRIMARIA, **kwargs):
        super().__init__(parent, width=width, height=32,
                         bg=COR_FUNDO, highlightthickness=0, **kwargs)
        self.w = width
        self.label = label
        self.color = color
        self.value = 0
        self.anim_value = 0
        self._render()

    def set_value(self, v):
        self.value = max(0, min(100, v))
        self._animate()

    def _animate(self):
        if abs(self.anim_value - self.value) > 0.5:
            self.anim_value += (self.value - self.anim_value) * 0.15
            self._render()
            self.after(20, self._animate)
        else:
            self.anim_value = self.value
            self._render()

    def _render(self):
        self.delete("all")
        self.create_rectangle(0, 10, self.w, 24,
                              fill=COR_PAINEL, outline=COR_BORDA, width=1)
        fill_w = int(self.w * self.anim_value / 100)
        if fill_w > 2:
            self.create_rectangle(2, 12, fill_w - 2, 22,
                                  fill=COR_TEXTO_DIM, outline="")
            self.create_rectangle(2, 12, fill_w - 2, 22,
                                  fill=self.color, outline="")
            if fill_w > 4:
                self.create_line(2, 13, fill_w - 2, 13, fill=COR_GLOW, width=1)
        txt = f"{self.label}  {self.anim_value:.0f}%"
        self.create_text(self.w // 2 + 1, 17 + 1, text=txt,
                         fill="#000000", font=("Consolas", 10, "bold"))
        self.create_text(self.w // 2, 17, text=txt,
                         fill="white", font=("Consolas", 10, "bold"))


class ParticleBackground(Canvas):
    def __init__(self, parent, width=950, height=700, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=COR_FUNDO, highlightthickness=0, **kwargs)
        self.w = width
        self.h = height
        self.particles = []
        self.scan_y = 0
        self._init_particles()
        self._animate()

    def _init_particles(self):
        for _ in range(60):
            self.particles.append({
                'x': random.uniform(0, self.w),
                'y': random.uniform(0, self.h),
                'vx': random.uniform(-0.3, 0.3),
                'vy': random.uniform(-0.3, 0.3),
                'size': random.uniform(1, 3),
                'brightness': random.randint(40, 180),
                'pulse': random.uniform(0, math.pi * 2),
            })

    def _animate(self):
        self.delete("all")
        for x in range(0, self.w, 80):
            self.create_line(x, 0, x, self.h, fill="#030d14", width=1)
        for y in range(0, self.h, 80):
            self.create_line(0, y, self.w, y, fill="#030d14", width=1)
        self.scan_y = (self.scan_y + 2) % self.h
        for i in range(3):
            alpha = max(0, 80 - i * 25)
            self.create_line(0, self.scan_y - i, self.w, self.scan_y - i,
                             fill=f"#00{alpha:02x}{min(alpha+20,255):02x}", width=1)
        for p in self.particles:
            p['x'] = (p['x'] + p['vx']) % self.w
            p['y'] = (p['y'] + p['vy']) % self.h
            p['pulse'] += 0.04
            b = int(p['brightness'] * (0.6 + 0.4 * math.sin(p['pulse'])))
            b = min(b, 255)
            col = f"#00{b:02x}{min(b+30,255):02x}"
            r = p['size']
            self.create_oval(p['x']-r, p['y']-r, p['x']+r, p['y']+r,
                             fill=col, outline="")
        for i, p1 in enumerate(self.particles):
            for p2 in self.particles[i+1:i+6]:
                dx = p1['x'] - p2['x']
                dy = p1['y'] - p2['y']
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < 100:
                    alpha = int(30 * (1 - dist/100))
                    self.create_line(p1['x'], p1['y'], p2['x'], p2['y'],
                                     fill=f"#00{alpha:02x}{min(alpha+10,255):02x}", width=1)
        self.after(40, self._animate)


class WaveVisualizer(Canvas):
    def __init__(self, parent, width=500, height=100, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=COR_FUNDO, highlightthickness=0, **kwargs)
        self.w = width
        self.h = height
        self.t = 0
        self.active = False
        self._draw()

    def set_active(self, state):
        self.active = state

    def _draw(self):
        self.delete("all")
        cx = self.h // 2
        n_bars = 48
        bar_w = self.w / n_bars
        for i in range(n_bars):
            x = i * bar_w + bar_w / 2
            if self.active:
                amp = (math.sin(self.t * 0.15 + i * 0.4) * 0.4 +
                       math.sin(self.t * 0.23 + i * 0.25) * 0.3 +
                       math.sin(self.t * 0.07 + i * 0.6) * 0.3)
                amp = abs(amp)
                h_bar = max(4, amp * cx * 1.8)
            else:
                amp = math.sin(self.t * 0.03 + i * 0.3) * 0.15 + 0.05
                h_bar = max(3, abs(amp) * cx * 0.8)
            ratio = h_bar / cx
            r_val = int(min(ratio * 255, 255))
            b_val = min(int(220 + h_bar * 2), 255)
            color = f"#{r_val:02x}{b_val:02x}ff" if ratio > 0.6 else f"#00{b_val:02x}ff"
            self.create_rectangle(x - bar_w*0.3, cx - h_bar, x + bar_w*0.3, cx,
                                  fill=color, outline="")
            self.create_rectangle(x - bar_w*0.3, cx, x + bar_w*0.3, cx + h_bar,
                                  fill=color, outline="")
        self.create_line(0, cx, self.w, cx, fill=COR_BORDA, width=1)
        self.t += 1
        self.after(40, self._draw)


class RadarHud(Canvas):
    def __init__(self, parent, size=120, **kwargs):
        super().__init__(parent, width=size, height=size,
                         bg=COR_PAINEL, highlightthickness=1,
                         highlightbackground=COR_BORDA, **kwargs)
        self.size = size
        self.cx = size // 2
        self.cy = size // 2
        self.angle = 0
        self.blips = []
        self._spawn_blips()
        self._draw()

    def _spawn_blips(self):
        self.blips = []
        for _ in range(5):
            r = random.uniform(10, self.size * 0.42)
            a = random.uniform(0, 2 * math.pi)
            self.blips.append({'r': r, 'a': a, 'life': random.uniform(0, 1)})

    def _draw(self):
        self.delete("all")
        cx, cy, s = self.cx, self.cy, self.size
        for r in [s*0.15, s*0.28, s*0.42]:
            self.create_oval(cx-r, cy-r, cx+r, cy+r, outline=COR_TEXTO_DIM, width=1)
        self.create_line(cx, cy-s*0.45, cx, cy+s*0.45, fill=COR_TEXTO_DIM, width=1)
        self.create_line(cx-s*0.45, cy, cx+s*0.45, cy, fill=COR_TEXTO_DIM, width=1)
        sweep_end_x = cx + s*0.42 * math.cos(math.radians(self.angle))
        sweep_end_y = cy + s*0.42 * math.sin(math.radians(self.angle))
        self.create_line(cx, cy, sweep_end_x, sweep_end_y, fill=COR_PRIMARIA, width=2)
        for i in range(30):
            a = self.angle - i * 2
            alpha = max(0, 50 - i * 2)
            col = f"#00{alpha:02x}{min(alpha+20,255):02x}"
            x = cx + s*0.42 * math.cos(math.radians(a))
            y = cy + s*0.42 * math.sin(math.radians(a))
            self.create_line(cx, cy, x, y, fill=col, width=1)
        for b in self.blips:
            b['life'] = (b['life'] + 0.01) % 1.0
            bx = cx + b['r'] * math.cos(b['a'])
            by = cy + b['r'] * math.sin(b['a'])
            alpha = int(200 * (1 - b['life']))
            col = f"#{alpha:02x}ff{alpha:02x}"
            self.create_oval(bx-3, by-3, bx+3, by+3, fill=col, outline="white", width=1)
        self.create_oval(cx-3, cy-3, cx+3, cy+3, fill=COR_PRIMARIA, outline="white", width=1)
        self.angle = (self.angle + 3) % 360
        self.after(40, self._draw)


class DataMatrix(Canvas):
    def __init__(self, parent, width=200, height=120, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=COR_PAINEL, highlightthickness=1,
                         highlightbackground=COR_BORDA, **kwargs)
        self.w = width
        self.h = height
        self.grid = [[random.random() for _ in range(10)] for _ in range(6)]
        self.t = 0
        self._draw()

    def _draw(self):
        self.delete("all")
        self.t += 1
        cols, rows = 10, 6
        cw = self.w // cols
        rh = self.h // rows
        for r in range(rows):
            for c in range(cols):
                val = (self.grid[r][c] + self.t * 0.008 + r*0.1 + c*0.07) % 1.0
                self.grid[r][c] = val
                b = min(int(val * 200 + 20), 255)
                char = random.choice("01") if random.random() < 0.05 else ("1" if val > 0.5 else "0")
                col = f"#00{b:02x}{min(b+40,255):02x}"
                x = c * cw + cw // 2
                y = r * rh + rh // 2
                self.create_text(x, y, text=char, fill=col, font=("Consolas", 9, "bold"))
        self.after(120, self._draw)


class NivelAcessoWidget(Canvas):
    def __init__(self, parent, width=200, **kwargs):
        super().__init__(parent, width=width, height=80,
                         bg=COR_PAINEL, highlightthickness=1,
                         highlightbackground=COR_BORDA, **kwargs)
        self.w = width
        self.nivel = 1
        self.pulse = 0
        self._draw()

    def set_nivel(self, nivel):
        self.nivel = nivel
        self._draw()

    def _draw(self):
        self.delete("all")
        self.pulse += 1
        p = 0.5 + 0.5 * math.sin(self.pulse * 0.07)
        protocolo, role, cor = definir_status_seguranca(self.nivel)

        self.create_rectangle(0, 0, self.w, 80, fill=COR_PAINEL, outline="")

        seg_w = (self.w - 20) // 6
        for i in range(6):
            x0 = 10 + i * (seg_w + 2)
            x1 = x0 + seg_w
            filled = (i + 1) <= self.nivel
            fill_col = cor if filled else COR_TEXTO_DIM
            if filled and i + 1 == self.nivel:
                alpha_extra = int(p * 40)
                try:
                    r = int(cor[1:3], 16)
                    g = int(cor[3:5], 16)
                    b = int(cor[5:7], 16)
                    r2 = min(r + alpha_extra, 255)
                    g2 = min(g + alpha_extra, 255)
                    b2 = min(b + alpha_extra, 255)
                    fill_col = f"#{r2:02x}{g2:02x}{b2:02x}"
                except Exception:
                    pass
            self.create_rectangle(x0, 30, x1, 50, fill=fill_col, outline=COR_BORDA, width=1)

        self.create_text(self.w // 2, 10, text=f"NÍV.{self.nivel}  {role}",
                         fill=cor, font=("Consolas", 9, "bold"), anchor="center")
        self.create_text(self.w // 2, 64, text=protocolo,
                         fill=COR_TEXTO_DIM, font=("Consolas", 8), anchor="center")

        self.after(50, self._draw)


def hud_separator_glow(parent):
    f = ctk.CTkFrame(parent, height=2, fg_color=COR_BORDA)
    f.pack(fill="x", padx=24, pady=8)

def jarvis_botao_premium(parent, text, command, width=240, height=48, cor=COR_PRIMARIA):
    btn = ctk.CTkButton(
        parent, text=text, command=command,
        width=width, height=height,
        font=FONTE_BOTAO,
        fg_color="transparent",
        border_width=2,
        border_color=cor,
        text_color=cor,
        hover_color=COR_TEXTO_DIM,
        corner_radius=2
    )
    return btn

def criar_painel_lateral_ultra(parent):
    frame = ctk.CTkFrame(parent, fg_color=COR_PAINEL,
                         border_width=2, border_color=COR_BORDA,
                         width=220, corner_radius=0)
    frame.pack_propagate(False)

    header = ctk.CTkFrame(frame, fg_color=COR_TEXTO_DIM, corner_radius=0, height=36)
    header.pack(fill="x")
    ctk.CTkLabel(header, text="◈ TELEMETRIA ◈",
                 font=FONTE_HUD, text_color=COR_PRIMARIA).pack(pady=8)

    hud_separator_glow(frame)

    labels = {}
    for nome, icone in [("CPU", "⚙"), ("RAM", "▣"), ("REDE", "↕"), ("TEMP", "℃")]:
        lbl = ctk.CTkLabel(frame, text=f"{icone}  {nome}: --",
                           font=FONTE_PEQUENA, text_color=COR_PRIMARIA, anchor="w")
        lbl.pack(anchor="w", padx=20, pady=3)
        labels[nome] = lbl

    hud_separator_glow(frame)

    ctk.CTkLabel(frame, text="◈ CLIMA LOCAL ◈",
                 font=FONTE_HUD, text_color=COR_OURO).pack(pady=4)
    clima_lbl = ctk.CTkLabel(frame, text="--",
                             font=FONTE_PEQUENA, text_color=COR_VERDE)
    clima_lbl.pack(padx=20, pady=4)
    labels["CLIMA"] = clima_lbl

    hud_separator_glow(frame)

    ctk.CTkLabel(frame, text="◈ RADAR ◈",
                 font=("Consolas", 9, "bold"), text_color=COR_TEXTO_DIM).pack(pady=(4, 2))
    radar = RadarHud(frame, size=110)
    radar.pack(pady=4)

    hud_separator_glow(frame)

    status_frame = ctk.CTkFrame(frame, fg_color="transparent")
    status_frame.pack(pady=8)
    ctk.CTkLabel(status_frame, text="●", font=("Arial", 16),
                 text_color=COR_VERDE).pack(side="left", padx=2)
    ctk.CTkLabel(status_frame, text="ONLINE",
                 font=FONTE_PEQUENA, text_color=COR_VERDE).pack(side="left")

    return frame, labels


app = ctk.CTk()
app.update_idletasks()
largura = app.winfo_screenwidth()
altura = app.winfo_screenheight()
app.geometry(f"{largura}x{altura}+0+0")
app.state("zoomed")
app.update()

ESCALA_X = largura / 1920
ESCALA_Y = altura / 1080
def ex(v): return int(v * ESCALA_X)
def ey(v): return int(v * ESCALA_Y)
app.title("J.A.R.V.I.S — Advanced Intelligence System")
app.configure(fg_color=COR_FUNDO)
ctk.set_appearance_mode("dark")


barra_progresso = None
lbl_cpu = None
lbl_ram = None
lbl_clima = None
bar_cpu = None
bar_ram = None
chart_cpu = None
chart_ram = None
titulo_seguranca = None
label_qr = None
wave_viz = None
noticias_box = None
lbl_noticias_update = None
tempo_box = None
lbl_tempo_update = None

nivel_widget_seg  = None
nivel_widget_chat = None
nivel_widget_voz  = None
nivel_widget_menu = None
lbl_nivel_chat    = None
lbl_nivel_voz     = None
lbl_nivel_menu    = None


def carregar_noticias():
    def fetch():
        try:
            import xml.etree.ElementTree as ET
            feeds = [
                "https://feeds.feedburner.com/PublicoRSS",
                "https://www.rtp.pt/noticias/rss/",
                "https://observador.pt/feed/",
            ]
            items_total = []
            for feed_url in feeds:
                try:
                    r = requests.get(feed_url, timeout=6)
                    root = ET.fromstring(r.content)
                    items = root.findall(".//item")[:4]
                    items_total.extend(items)
                    if len(items_total) >= 8:
                        break
                except Exception:
                    continue

            noticias_box.configure(state="normal")
            noticias_box.delete("1.0", "end")

            if items_total:
                for i, item in enumerate(items_total[:8]):
                    titulo_n = item.findtext("title", "").strip()
                    if titulo_n:
                        noticias_box.insert("end", f"◈ {titulo_n}\n\n")
            else:
                noticias_box.insert("end", "⚠ Sem notícias disponíveis.")

            lbl_noticias_update.configure(text=f"Atualizado: {time.strftime('%H:%M')}")
            noticias_box.configure(state="disabled")
        except Exception:
            noticias_box.configure(state="normal")
            noticias_box.delete("1.0", "end")
            noticias_box.insert("end", "⚠ Erro ao carregar notícias.")
            noticias_box.configure(state="disabled")

        app.after(300000, carregar_noticias)

    threading.Thread(target=fetch, daemon=True).start()


def carregar_tempo():
    def fetch():
        try:
            geo_url = "https://geocoding-api.open-meteo.com/v1/search?name=Lisboa&count=1&language=pt"
            geo = requests.get(geo_url, timeout=5).json()
            res = geo["results"][0]
            lat, lon = res["latitude"], res["longitude"]

            meteo_url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weathercode"
                f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
                f"&timezone=auto&forecast_days=4"
            )
            meteo = requests.get(meteo_url, timeout=5).json()
            atual = meteo["current"]
            diario = meteo["daily"]

            codigos = {
                0: "☀ Céu limpo", 1: "🌤 Principalmente limpo",
                2: "⛅ Parcialmente nublado", 3: "☁ Nublado",
                45: "🌫 Nevoeiro", 61: "🌧 Chuva leve",
                63: "🌧 Chuva moderada", 65: "🌧 Chuva forte",
                80: "🌦 Aguaceiros", 95: "⛈ Trovoada"
            }
            cond = codigos.get(atual["weathercode"], "Condição desconhecida")

            texto = (
                f"◈ LISBOA — AGORA\n\n"
                f"🌡  {atual['temperature_2m']}°C\n"
                f"💧  Humidade: {atual['relative_humidity_2m']}%\n"
                f"💨  Vento: {atual['wind_speed_10m']} km/h\n"
                f"    {cond}\n\n"
                f"◈ PRÓXIMOS DIAS\n\n"
            )
            dias_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
            import datetime
            for i in range(4):
                data_str = diario["time"][i]
                data_obj = datetime.datetime.strptime(data_str, "%Y-%m-%d")
                dia_sem = dias_semana[data_obj.weekday()]
                tmax = diario["temperature_2m_max"][i]
                tmin = diario["temperature_2m_min"][i]
                chuva = diario["precipitation_sum"][i]
                texto += f"  {dia_sem} {data_obj.strftime('%d/%m')}\n"
                texto += f"  ↑{tmax}° ↓{tmin}°  🌧{chuva}mm\n\n"

            tempo_box.configure(state="normal")
            tempo_box.delete("1.0", "end")
            tempo_box.insert("end", texto)
            lbl_tempo_update.configure(text=f"Atualizado: {time.strftime('%H:%M')}")
            tempo_box.configure(state="disabled")

        except Exception:
            tempo_box.configure(state="normal")
            tempo_box.delete("1.0", "end")
            tempo_box.insert("end", "⚠ Erro ao carregar meteorologia.")
            tempo_box.configure(state="disabled")

        app.after(600000, carregar_tempo)

    threading.Thread(target=fetch, daemon=True).start()


def atualizar_widgets_nivel():
    protocolo, role, cor = definir_status_seguranca(NIVEL_ACESSO_ATUAL)
    texto_nivel = f"NÍV.{NIVEL_ACESSO_ATUAL}  {protocolo} — {role}"

    for widget in [nivel_widget_seg, nivel_widget_chat, nivel_widget_voz, nivel_widget_menu]:
        if widget:
            widget.set_nivel(NIVEL_ACESSO_ATUAL)

    for lbl in [lbl_nivel_chat, lbl_nivel_voz, lbl_nivel_menu]:
        if lbl:
            lbl.configure(text=texto_nivel, text_color=cor)


def atualizar_graficos():
    cpu, ram, clima = obter_telemetria()
    lbl_cpu.configure(text=f"⚙  CPU  {cpu:.0f}%")
    lbl_ram.configure(text=f"▣  RAM  {ram:.0f}%")
    lbl_clima.configure(text=f"{clima}")
    chart_cpu.update_value(cpu)
    chart_ram.update_value(ram)
    bar_cpu.set_value(cpu)
    bar_ram.set_value(ram)
    if ecra_seguranca.winfo_ismapped():
        app.after(1000, atualizar_graficos)


SENHAS_NIVEL = {
    "jarvis":  5,
    "stark":   4,
    "pepper":  3,
    "guest":   2,
}


LOGS_JARVIS = [
    "[*] KERNEL ONLINE. INICIANDO SEQUÊNCIA...",
    "[*] CARREGANDO REDE NEURAL ARTIFICIAL...",
    "[*] VERIFICANDO NÍVEIS DO REATOR ARC... ESTÁVEL.",
    "[!] CALIBRANDO SENSORES DE RECONHECIMENTO...",
    "[*] IMPORTANDO MÓDULOS DE VOZ E SÍNTESE...",
    "[*] ACESSO A BANCO DE DADOS CLASSIFICADO: CONCEDIDO.",
    "[*] ATIVANDO PROTOCOLOS DE DEFESA...",
    "[!] DESCRIPTOGRAFANDO SISTEMA H.U.D...",
    "[*] ESTABELECENDO CONEXÃO VIA SATÉLITE...",
    "[*] VERIFICAÇÃO DE INTEGRIDADE DE SISTEMA: 100%."
]


def simulador_loading(progresso=0):
    if progresso == 0:

        terminal_loading.configure(state="normal")
        terminal_loading.delete("0.0", "end")
        terminal_loading.configure(state="disabled")

    if progresso <= 100:

        barra_loading.set(progresso / 100)
        lbl_loading_porcentagem.configure(text=f"{progresso}% COMPLETO")


        barra_processamento.set(random.uniform(0.1, 1.0))


        if progresso % 10 == 0 and progresso < 100:
            indice_log = (progresso // 10) % len(LOGS_JARVIS)
            novo_log = LOGS_JARVIS[indice_log]

            lbl_loading_status.configure(text=f"◈ {novo_log.replace('[*]', '').replace('[!]', '').strip()} ◈")

            terminal_loading.configure(state="normal")
            terminal_loading.insert("end", f"> {novo_log}\n")
            terminal_loading.see("end")  # Faz scroll automático para o fundo
            terminal_loading.configure(state="disabled")


        app.after(40, lambda: simulador_loading(progresso + 1))
    else:

        ecra_loading.pack_forget()
        threading.Thread(target=fase_biometria, daemon=True).start()


def verificar_senha():
    global NIVEL_ACESSO_ATUAL
    senha = entrada_senha.get().strip().lower()
    nivel = SENHAS_NIVEL.get(senha, 0)
    if nivel >= 2:
        NIVEL_ACESSO_ATUAL = nivel
        label_erro.configure(text="")
        ecra_login.pack_forget()


        ecra_loading.pack(expand=True, fill="both")
        simulador_loading(0)
    else:
        label_erro.configure(text="⚠ ACESSO NEGADO — CREDENCIAIS INVÁLIDAS")


def fase_biometria():
    app.after(0, _iniciar_ecra_seguranca)
    servidor_biometria.evento_validado.wait()
    app.after(0, apos_validacao)

def _iniciar_ecra_seguranca():
    ecra_seguranca.pack(expand=True, fill="both")
    barra_progresso.start()
    label_qr.configure(text="◈  ESCANEIE O QR CODE NO SEU TELEMÓVEL  ◈")
    servidor_biometria.link_qr(label_qr)
    atualizar_graficos()
    atualizar_widgets_nivel()

def apos_validacao():
    barra_progresso.stop()
    ecra_seguranca.pack_forget()
    protocolo, role, _ = definir_status_seguranca(NIVEL_ACESSO_ATUAL)
    jarvis_falar(f"Autenticação confirmada. Bem-vindo, {role}. {protocolo} ativo.")
    atualizar_widgets_nivel()
    carregar_noticias()
    carregar_tempo()
    mostrar_ecra_niveis()


def processar_comando_texto(texto):
    if not texto:
        return

    protocolo, role, cor = definir_status_seguranca(NIVEL_ACESSO_ATUAL)
    caixa_chat.insert("end", f"\n  TU ({role} | NÍV.{NIVEL_ACESSO_ATUAL})  »  {texto}\n", "user")

    pode, nivel_min = nivel_pode_executar(texto, NIVEL_ACESSO_ATUAL)
    if not pode:
        _, role_min, _ = definir_status_seguranca(nivel_min)
        resposta = f"⚠ ACESSO NEGADO — requer nível {nivel_min} ({role_min})."

    elif texto.lower().startswith("calcular:") or texto.lower().startswith("calc:"):
        expressao = texto.split(":", 1)[1].strip()
        try:
            resultado = eval(expressao)
            resposta = f"◈ RESULTADO: {expressao} = {resultado}"
        except:
            resposta = "⚠ Expressão inválida. Exemplo: calc: 25 * 4 + 10"

    elif texto.lower().startswith("pesquisar:") or texto.lower().startswith("search:"):
        if NIVEL_ACESSO_ATUAL < 2:
            resposta = "⚠ Pesquisa requer nível 2+"
        else:
            query = texto.split(":", 1)[1].strip()
            resposta = pensar(f"Faz uma pesquisa sobre '{query}' e resume os pontos principais em português.")

    elif texto.lower() in ["noticias", "notícias", "news"]:
        if NIVEL_ACESSO_ATUAL < 2:
            resposta = "⚠ Notícias requer nível 2+"
        else:
            resposta = pensar("Quais são as principais notícias de hoje em Portugal e no mundo? Resume em tópicos.")

    elif texto.lower().startswith("traduzir:") or texto.lower().startswith("translate:"):
        if NIVEL_ACESSO_ATUAL < 3:
            resposta = "⚠ Tradutor requer nível 3+"
        else:
            partes = texto.split(":", 2)
            if len(partes) >= 3:
                lingua = partes[1].strip()
                conteudo = partes[2].strip()
                resposta = pensar(f"Traduz este texto para {lingua}, responde APENAS com a tradução: {conteudo}")
            else:
                resposta = "⚠ Formato: traduzir: inglês : texto a traduzir"

    elif texto.lower().startswith("resumir:") or texto.lower().startswith("resumo:"):
        if NIVEL_ACESSO_ATUAL < 3:
            resposta = "⚠ Resumidor requer nível 3+"
        else:
            conteudo = texto.split(":", 1)[1].strip()
            resposta = pensar(f"Resume este texto de forma clara e concisa em português: {conteudo}")

    elif texto.lower().startswith("email:"):
        if NIVEL_ACESSO_ATUAL < 3:
            resposta = "⚠ Gerador de emails requer nível 3+"
        else:
            assunto = texto.split(":", 1)[1].strip()
            resposta = pensar(
                f"Escreve um email profissional em português sobre: {assunto}. Inclui assunto, corpo e despedida.")

    elif texto.lower().startswith("converter:") or texto.lower().startswith("conv:"):
        if NIVEL_ACESSO_ATUAL < 3:
            resposta = "⚠ Conversor requer nível 3+"
        else:
            expressao = texto.split(":", 1)[1].strip()
            resposta = pensar(f"Converte esta unidade e explica o resultado: {expressao}.")

    elif texto.lower().startswith("analisar:") or texto.lower().startswith("analyze:"):
        if NIVEL_ACESSO_ATUAL < 4:
            resposta = "⚠ Analisador de código requer nível 4+"
        else:
            codigo = texto.split(":", 1)[1].strip()
            resposta = pensar(
                f"Analisa este código em detalhe: explica o que faz, complexidade, boas práticas e melhorias:\n{codigo}")

    elif texto.lower().startswith("password:") or texto.lower().startswith("pass:"):
        if NIVEL_ACESSO_ATUAL < 4:
            resposta = "⚠ Gerador de passwords requer nível 4+"
        else:
            import random as rnd, string
            partes = texto.split(":", 1)[1].strip()
            try:
                tamanho = int(partes)
            except:
                tamanho = 16
            chars = string.ascii_letters + string.digits + "!@#$%^&*"
            pwd = "".join(rnd.choices(chars, k=tamanho))
            resposta = f"◈ PASSWORD GERADA ({tamanho} chars):\n{pwd}\n\n⚠ Guarda num local seguro."

    elif texto.lower().startswith("relatorio:") or texto.lower().startswith("relatório:"):
        if NIVEL_ACESSO_ATUAL < 5:
            resposta = "⚠ Relatórios requer nível 5+"
        else:
            partes = texto.split(":", 1)
            if len(partes) >= 2 and partes[1].strip():
                from core.relatorio import gerar_relatorio_pt
                titulo = partes[1].strip()
                caixa_chat.insert("end", "\n  JARVIS  »  A gerar conteúdo do relatório...\n", "jarvis")
                caixa_chat.update()
                conteudo_gerado = pensar(
                    f"Gera um relatório completo e detalhado sobre o tema: '{titulo}'.\n"
                    f"Estrutura obrigatória:\n"
                    f"- INTRODUÇÃO\n"
                    f"- DESENVOLVIMENTO (com subtópicos relevantes)\n"
                    f"- CONCLUSÃO\n"
                    f"- RECOMENDAÇÕES\n\n"
                    f"Usa linguagem formal e profissional em português de Portugal.\n"
                    f"Cada secção deve ter pelo menos 3-4 parágrafos detalhados.\n"
                    f"Responde APENAS com o conteúdo do relatório, sem comentários extra."
                )
                caminho = gerar_relatorio_pt(titulo, conteudo_gerado)
                resposta = f"✔ Relatório '{titulo}' gerado e aberto: {caminho}"
            else:
                resposta = "⚠ Formato: relatorio: Tema do Relatório"

    elif texto.lower().startswith("ficheiros:") or texto.lower().startswith("files:"):
        if NIVEL_ACESSO_ATUAL < 5:
            resposta = "⚠ Monitor de ficheiros requer nível 5+"
        else:
            import os
            pasta = texto.split(":", 1)[1].strip() or "."
            try:
                ficheiros = os.listdir(pasta)
                total = len(ficheiros)
                lista = "\n".join(f"  • {f}" for f in ficheiros[:20])
                resposta = f"◈ PASTA: {os.path.abspath(pasta)}\n{total} ficheiros:\n{lista}"
                if total > 20:
                    resposta += f"\n  ... e mais {total - 20} ficheiros"
            except:
                resposta = f"⚠ Pasta '{pasta}' não encontrada."


    elif texto.lower() in ["ajuda", "help", "comandos", "o que podes fazer"]:

        cmds = ["   ╔═════════════════ COMANDOS J.A.R.V.I.S. ═════════════════╗\n"]

        cmds.append("  calc: 25 * 4          → Calculadora básica")



        if NIVEL_ACESSO_ATUAL >= 2:
            cmds.append("  que horas são         → Ver hora atual e data")

            cmds.append("  volume [subir/baixar] → Controlar o som (ou 'silencia')")

            cmds.append("  brilho [subir/baixar] → Controlar o brilho do ecrã")

            cmds.append("  abre [aplicação]      → Iniciar Chrome, Spotify, VSCode, etc.")

            cmds.append("  lista de apps         → Ver todas as aplicações registadas")

            cmds.append("  pesquisa [termo]      → Realizar pesquisa rápida no Google")

            cmds.append("  youtube [termo]       → Procurar vídeos diretamente no YouTube")

            cmds.append("  tempo em [cidade]     → Meteorologia em tempo real (Open-Meteo)")

            cmds.append("  lembra-me de [...]     → Criar um alarme/lembrete em minutos")

            cmds.append("  estado do sistema     → Monitorizar uso de CPU, RAM e Disco")

            cmds.append("  noticias              → Notícias do dia")



        if NIVEL_ACESSO_ATUAL >= 3:
            cmds.append("  traduzir: en : texto  → Tradutor de Idiomas")

            cmds.append("  resumir: texto        → Resumidor de Textos")

            cmds.append("  email: assunto        → Gerar rascunho de e-mail profissional")

            cmds.append("  conv: 100km para mph  → Conversor de Unidades")



        if NIVEL_ACESSO_ATUAL >= 4:
            cmds.append("  analisar: código      → Analisador de Sintaxe")

            cmds.append("  pass: 20              → Gerador de Password Segura")



        if NIVEL_ACESSO_ATUAL >= 5:
            cmds.append("  relatorio: Tema       → Compilar e Gerar Documento Word")

            cmds.append("  ficheiros: pasta      → Explorador de Ficheiros do Sistema")

        cmds.append("\n   ╚═════════════════════════════════════════════════════════╝")

        resposta = "\n".join(cmds)

    elif texto.lower() in ["cls", "limpar", "limpar ecrã", "limpar ecra"]:
        caixa_chat.configure(state="normal")
        caixa_chat.delete("1.0", "end")
        caixa_chat.insert("end", "  ◈  ECRÃ LIMPO  ◈\n\n", "jarvis")
        caixa_chat.see("end")
        return

    elif texto.lower() in ["cls-m", "limpar memoria", "limpar memória", "cls memoria"]:
        from core.cerebro import limpar_memoria
        limpar_memoria()
        caixa_chat.configure(state="normal")
        caixa_chat.delete("1.0", "end")
        caixa_chat.insert("end", "  ◈  ECRÃ E MEMÓRIA LIMPOS  ◈\n\n", "jarvis")
        caixa_chat.see("end")
        return
    else:

        resposta = pensar(texto)

    caixa_chat.insert("end", f"\n  JARVIS  »  {resposta}\n\n", "jarvis")
    caixa_chat.see("end")


def enviar_mensagem_texto():
    texto = barra_texto.get()
    if not texto:
        return
    barra_texto.delete(0, "end")
    processar_comando_texto(texto)

def logica_conversa_continua():
    protocolo, role, _ = definir_status_seguranca(NIVEL_ACESSO_ATUAL)
    jarvis_falar(f"Modo de voz ativado. A ouvir, {role}.")
    if wave_viz:
        wave_viz.set_active(True)
    while True:
        texto_utilizador = ouvir_mic()
        if not texto_utilizador:
            continue
        if "desligar" in texto_utilizador or "parar" in texto_utilizador:
            jarvis_falar("Com certeza. Modo de voz encerrado.")
            if wave_viz:
                wave_viz.set_active(False)
            break
        pode, nivel_min = nivel_pode_executar(texto_utilizador, NIVEL_ACESSO_ATUAL)
        if not pode:
            _, role_min, _ = definir_status_seguranca(nivel_min)
            jarvis_falar(f"Acesso negado. Este comando requer nível {nivel_min}.")
        else:
            resposta_jarvis = pensar(texto_utilizador, callback_falar=jarvis_falar)
            jarvis_falar(resposta_jarvis)

def iniciar_escuta_thread():
    threading.Thread(target=logica_conversa_continua, daemon=True).start()

def abrir_modo_texto():
    ecra_inicial.pack_forget()
    ecra_voz.pack_forget()
    atualizar_widgets_nivel()
    ecra_chat.pack(expand=True, fill="both")

def abrir_modo_voz():
    ecra_inicial.pack_forget()
    ecra_chat.pack_forget()
    atualizar_widgets_nivel()
    ecra_voz.pack(expand=True, fill="both")

def voltar_menu():
    ecra_chat.pack_forget()
    ecra_voz.pack_forget()
    ecra_professor.pack_forget()
    atualizar_widgets_nivel()
    ecra_inicial.pack(expand=True, fill="both")

def abrir_modo_professor():
    ecra_inicial.pack_forget()
    ecra_chat.pack_forget()
    ecra_voz.pack_forget()
    ecra_professor.pack(expand=True, fill="both")

ferramenta_ativa = ""

def ativar_ferramenta(modo):
    global ferramenta_ativa
    ferramenta_ativa = modo
    nomes = {
        "corretor":  "⚙  CORRIGIR CÓDIGO — cola o código em baixo",
        "ficha":     "📄  GERAR FICHA — escreve o tema da ficha",
        "dashboard": "📊  DASHBOARD — escreve: Nome=nota, Nome=nota...",
        "voz":       "🎙  EXPLICADOR VOZ — escreve o conceito a explicar",
    }
    lbl_modo_prof.configure(text=f"◈  {nomes.get(modo, '')}  ◈")
    entrada_prof.delete(0, "end")
    entrada_prof.focus()

def executar_ferramenta_professor():
    texto = entrada_prof.get().strip()
    if not texto:
        return
    entrada_prof.delete(0, "end")
    caixa_prof.insert("end", f"\n  ◈  INPUT  »  {texto}\n", "titulo")

    if ferramenta_ativa == "corretor":
        resposta = pensar(
            f"És um professor de programação. Analisa este código, "
            f"diz se está correto, explica os erros se existirem "
            f"e sugere correções em português. Código:\n{texto}"
        )
    elif ferramenta_ativa == "ficha":
        resposta = pensar(
            f"Cria uma ficha de trabalho de programação sobre '{texto}'. "
            f"Inclui: título, 5 exercícios numerados com cotações, "
            f"espaço para respostas. Formato limpo."
        )
    elif ferramenta_ativa == "dashboard":
        try:
            pares = [p.strip() for p in texto.split(",")]
            notas = {}
            for par in pares:
                nome, nota = par.split("=")
                notas[nome.strip()] = float(nota.strip())
            media = sum(notas.values()) / len(notas)
            melhor = max(notas, key=notas.get)
            pior = min(notas, key=notas.get)
            aprovados = sum(1 for n in notas.values() if n >= 10)
            reprovados = len(notas) - aprovados
            resposta = (
                f"TURMA — {len(notas)} alunos\n"
                f"Média:       {media:.1f}\n"
                f"Melhor:      {melhor} ({notas[melhor]})\n"
                f"Mais baixo:  {pior} ({notas[pior]})\n"
                f"Aprovados:   {aprovados}\n"
                f"Reprovados:  {reprovados}"
            )
        except:
            resposta = "⚠ Formato incorreto. Usa: João=15, Maria=18, Pedro=10"
    elif ferramenta_ativa == "voz":
        resposta = pensar(
            f"Explica o conceito de programação '{texto}' "
            f"de forma simples e clara para alunos. "
            f"Usa exemplos práticos em Python."
        )
        threading.Thread(target=lambda: jarvis_falar(resposta), daemon=True).start()
    else:
        resposta = "⚠ Seleciona uma ferramenta primeiro."

    caixa_prof.insert("end", f"\n  JARVIS  »  {resposta}\n\n", "ok")
    caixa_prof.see("end")

def adaptar_menu_ao_nivel():
    if NIVEL_ACESSO_ATUAL >= 3:
        btn_modo_voz.pack(pady=8)
    else:
        btn_modo_voz.pack_forget()
    if NIVEL_ACESSO_ATUAL == 6:
        btn_professor.pack(pady=8)
    else:
        btn_professor.pack_forget()


ecra_loading = ctk.CTkFrame(app, fg_color=COR_FUNDO)


ctk.CTkLabel(
    ecra_loading,
    text="J.A.R.V.I.S. SYSTEM BOOT",
    font=("Bahnschrift", 24, "bold"),
    text_color=COR_SECUNDARIA
).pack(pady=(120, 10))


lbl_loading_status = ctk.CTkLabel(
    ecra_loading,
    text="◈ INICIANDO PROTOCOLOS... ◈",
    font=FONTE_HUD,
    text_color=COR_PRIMARIA
)
lbl_loading_status.pack(pady=(0, 20))


terminal_loading = ctk.CTkTextbox(
    ecra_loading,
    width=500,
    height=150,
    fg_color=COR_PAINEL,
    text_color=COR_PRIMARIA,
    border_color=COR_BORDA,
    border_width=1,
    font=("Consolas", 10),
    state="disabled"
)
terminal_loading.pack(pady=10)


barra_loading = ctk.CTkProgressBar(
    ecra_loading,
    width=500,
    height=12,
    progress_color=COR_PRIMARIA,
    fg_color=COR_PAINEL,
    border_width=1,
    border_color=COR_BORDA
)
barra_loading.set(0)
barra_loading.pack(pady=(20, 5))


barra_processamento = ctk.CTkProgressBar(
    ecra_loading,
    width=500,
    height=2,
    progress_color=COR_SECUNDARIA,
    fg_color=COR_PAINEL,
    mode="determinate"
)
barra_processamento.set(0)
barra_processamento.pack(pady=0)


lbl_loading_porcentagem = ctk.CTkLabel(
    ecra_loading,
    text="0% COMPLETO",
    font=FONTE_HUD,
    text_color=COR_PRIMARIA
)
lbl_loading_porcentagem.pack(pady=10)

ecra_login = ctk.CTkFrame(app, fg_color="transparent")
ecra_login.pack(expand=True, fill="both")

particle_bg = ParticleBackground(ecra_login, width=largura, height=altura)
particle_bg.place(x=0, y=0, relwidth=1, relheight=1)

col_login = ctk.CTkFrame(ecra_login, fg_color="transparent")
col_login.place(relx=0.5, rely=0.5, anchor="center")

painel_login = ctk.CTkFrame(col_login, fg_color="#020c14",
                             border_width=2, border_color=COR_BORDA, corner_radius=0)
painel_login.pack()

inner_login = ctk.CTkFrame(painel_login, fg_color="transparent")
inner_login.pack(padx=40, pady=30)

deco_top = ctk.CTkFrame(inner_login, fg_color="transparent")
deco_top.pack()
for i in range(3):
    ctk.CTkFrame(deco_top, width=80, height=2,
                 fg_color=COR_BORDA if i != 1 else COR_PRIMARIA).pack(side="left", padx=4)

ctk.CTkLabel(inner_login, text="J · A · R · V · I · S",
             font=("Bahnschrift", 42, "bold"), text_color=COR_PRIMARIA).pack(pady=8)
ctk.CTkLabel(inner_login, text="JUST A RATHER VERY INTELLIGENT SYSTEM",
             font=("Consolas", 11), text_color=COR_SECUNDARIA).pack()

class_frame = ctk.CTkFrame(inner_login, fg_color=COR_PAINEL,
                            border_width=1, border_color=COR_BORDA,
                            corner_radius=0, height=24)
class_frame.pack(fill="x", pady=(8, 4))
ctk.CTkLabel(class_frame,
             text="  ⚠  STARK INDUSTRIES — CLASSIFIED — SECURITY LEVEL: ALPHA  ⚠  ",
             font=("Consolas", 9), text_color=COR_ALERTA).pack(pady=4)

deco_bot = ctk.CTkFrame(inner_login, fg_color="transparent")
deco_bot.pack(pady=(4, 16))
for i in range(3):
    ctk.CTkFrame(deco_bot, width=80, height=2,
                 fg_color=COR_BORDA if i != 1 else COR_PRIMARIA).pack(side="left", padx=4)

arc_info_row = ctk.CTkFrame(inner_login, fg_color="transparent")
arc_info_row.pack(pady=8)

arc_login = ArcReactorUltra(arc_info_row, size=150)
arc_login.pack(side="left", padx=(0, 24))

info_col = ctk.CTkFrame(arc_info_row, fg_color="transparent")
info_col.pack(side="left", anchor="center")

ctk.CTkLabel(info_col, text="◈ NÍVEIS DE ACESSO ◈",
             font=("Consolas", 9, "bold"), text_color=COR_SECUNDARIA).pack(anchor="w", pady=(0, 6))
for senha_hint, nivel_hint, cor_hint in [
    ("••••••• (6)", "TEACHER", "#FFD700"),
    ("••••••• (5)", "ADMIN",    "#00E5FF"),
    ("••••••• (4)",  "OPERATOR", "#00FF99"),
    ("••••••• (3)",  "ANALYST",  "#FFD700"),
    ("••••••• (2)",  "GUEST",    "#0099DD"),
]:
    rh = ctk.CTkFrame(info_col, fg_color="transparent")
    rh.pack(anchor="w", pady=2)
    ctk.CTkLabel(rh, text=f"● {senha_hint}  →  ",
                 font=("Consolas", 9), text_color=COR_TEXTO_DIM).pack(side="left")
    ctk.CTkLabel(rh, text=nivel_hint,
                 font=("Consolas", 9, "bold"), text_color=cor_hint).pack(side="left")

ctk.CTkFrame(inner_login, height=1, fg_color=COR_BORDA).pack(fill="x", pady=12)
ctk.CTkLabel(inner_login, text="◈ AUTENTICAÇÃO PRIMÁRIA ◈",
             font=FONTE_HUD, text_color=COR_SECUNDARIA).pack(pady=(0, 10))

entrada_senha = ctk.CTkEntry(
    inner_login, placeholder_text="PALAVRA-PASSE DE ACESSO",
    show="●", width=300, height=46,
    font=FONTE_HUD,
    fg_color=COR_PAINEL,
    border_color=COR_BORDA,
    border_width=2,
    text_color=COR_PRIMARIA,
    placeholder_text_color=COR_TEXTO_DIM,
    corner_radius=2
)
entrada_senha.pack(pady=8)
entrada_senha.bind("<Return>", lambda e: verificar_senha())

jarvis_botao_premium(inner_login, "[ AUTENTICAR ]", verificar_senha,
                     width=300, height=46).pack(pady=8)

label_erro = ctk.CTkLabel(inner_login, text="", font=FONTE_PEQUENA, text_color=COR_ALERTA)
label_erro.pack(pady=6)

ctk.CTkLabel(inner_login, text="STARK INDUSTRIES  ·  CONFIDENTIAL  ·  v4.5 ULTRA",
             font=("Consolas", 9), text_color=COR_TEXTO_DIM).pack(pady=(8, 0))


ecra_seguranca = ctk.CTkFrame(app, fg_color="transparent")

header_seg = ctk.CTkFrame(ecra_seguranca, fg_color=COR_PAINEL,
                          corner_radius=0, border_width=2, border_color=COR_BORDA, height=50)
header_seg.pack(fill="x", padx=24, pady=(20, 0))
header_seg.pack_propagate(False)

titulo_seguranca = ctk.CTkLabel(
    header_seg, text="◈  PROTOCOLO DE SEGURANÇA BIOMÉTRICA ATIVO  ◈",
    font=FONTE_TITULO, text_color=COR_PRIMARIA
)
titulo_seguranca.pack(side="left", padx=20)
ctk.CTkLabel(header_seg, text="NÍVEL: MÁXIMO",
             font=FONTE_PEQUENA, text_color=COR_OURO).pack(side="right", padx=20)

hud_separator_glow(ecra_seguranca)

corpo_seg = ctk.CTkFrame(ecra_seguranca, fg_color="transparent")
corpo_seg.pack(expand=True, fill="both", padx=24)

painel_lat, lat_labels = criar_painel_lateral_ultra(corpo_seg)
painel_lat.pack(side="left", fill="y", pady=12, padx=(0, 20))
lbl_cpu = lat_labels["CPU"]
lbl_ram = lat_labels["RAM"]
lbl_clima = lat_labels["CLIMA"]

centro_seg = ctk.CTkFrame(corpo_seg, fg_color="transparent")
centro_seg.pack(side="left", expand=True, fill="both")

arc_seg = ArcReactorUltra(centro_seg, size=150)
arc_seg.pack(pady=(10, 4))

ctk.CTkLabel(centro_seg, text="AGUARDANDO VALIDAÇÃO BIOMÉTRICA",
             font=FONTE_HUD, text_color=COR_SECUNDARIA).pack(pady=4)

nivel_widget_seg = NivelAcessoWidget(centro_seg, width=360)
nivel_widget_seg.pack(pady=(4, 8))

barra_progresso = ctk.CTkProgressBar(
    centro_seg, orientation="horizontal",
    mode="indeterminate", width=360, height=8,
    fg_color=COR_PAINEL, progress_color=COR_PRIMARIA,
    corner_radius=0, border_width=1, border_color=COR_BORDA
)
barra_progresso.pack(pady=8)

ctk.CTkLabel(centro_seg, text="CPU  —  HISTÓRICO",
             font=("Consolas", 9), text_color=COR_TEXTO_DIM).pack(anchor="w", padx=12)
chart_cpu = HudLineChart(centro_seg, label="CPU", width=360, height=55, color=COR_PRIMARIA)
chart_cpu.pack(pady=(0, 4), padx=12)

ctk.CTkLabel(centro_seg, text="RAM  —  HISTÓRICO",
             font=("Consolas", 9), text_color=COR_TEXTO_DIM).pack(anchor="w", padx=12)
chart_ram = HudLineChart(centro_seg, label="RAM", width=360, height=55, color=COR_OURO)
chart_ram.pack(pady=(0, 6), padx=12)

bar_cpu = HudBarPremium(centro_seg, label="CPU", width=360, color=COR_PRIMARIA)
bar_cpu.pack(pady=2)
bar_ram = HudBarPremium(centro_seg, label="RAM", width=360, color=COR_OURO)
bar_ram.pack(pady=2)

hud_separator_glow(centro_seg)

label_qr = ctk.CTkLabel(
    centro_seg, text="◈  A GERAR TÚNEL SEGURO...  ◈",
    font=FONTE_PEQUENA, text_color=COR_VERDE
)
label_qr.pack(pady=8)


ecra_professor = ctk.CTkFrame(app, fg_color="transparent")

topo_prof = ctk.CTkFrame(ecra_professor, fg_color=COR_PAINEL,
                          corner_radius=0, border_width=2,
                          border_color=COR_PROFESSOR, height=50)
topo_prof.pack(fill="x", padx=24, pady=(20, 0))
topo_prof.pack_propagate(False)

jarvis_botao_premium(topo_prof, "◀ VOLTAR", voltar_menu,
                     width=120, height=36, cor=COR_PROFESSOR).pack(side="left", padx=12, pady=7)
ctk.CTkLabel(topo_prof, text="◈  MODO PROFESSOR  —  ACESSO NÍVEL 6  ◈",
             font=FONTE_HUD, text_color=COR_PROFESSOR).pack(side="left", padx=24)
ctk.CTkLabel(topo_prof, text="● TEACHER",
             font=FONTE_PEQUENA, text_color=COR_PROFESSOR).pack(side="right", padx=20)

corpo_prof = ctk.CTkFrame(ecra_professor, fg_color="transparent")
corpo_prof.pack(expand=True, fill="both", padx=24, pady=16)

col_esq_prof = ctk.CTkFrame(corpo_prof, fg_color=COR_PAINEL,
                              border_width=2, border_color=COR_PROFESSOR,
                              width=320, corner_radius=0)
col_esq_prof.pack(side="left", fill="y", padx=(0, 16))
col_esq_prof.pack_propagate(False)

ctk.CTkLabel(col_esq_prof, text="◈ FERRAMENTAS ◈",
             font=FONTE_HUD, text_color=COR_PROFESSOR).pack(pady=16)
ctk.CTkFrame(col_esq_prof, height=1, fg_color=COR_PROFESSOR).pack(fill="x", padx=12, pady=4)

jarvis_botao_premium(col_esq_prof, "⚙  CORRIGIR CÓDIGO",
                     lambda: ativar_ferramenta("corretor"),
                     width=280, height=52, cor=COR_PROFESSOR).pack(pady=10, padx=16)
jarvis_botao_premium(col_esq_prof, "📄  GERAR FICHA WORD",
                     lambda: ativar_ferramenta("ficha"),
                     width=280, height=52, cor=COR_PROFESSOR).pack(pady=10, padx=16)
jarvis_botao_premium(col_esq_prof, "📊  DASHBOARD TURMA",
                     lambda: ativar_ferramenta("dashboard"),
                     width=280, height=52, cor=COR_PROFESSOR).pack(pady=10, padx=16)
jarvis_botao_premium(col_esq_prof, "🎙  EXPLICADOR VOZ",
                     lambda: ativar_ferramenta("voz"),
                     width=280, height=52, cor=COR_PROFESSOR).pack(pady=10, padx=16)

ctk.CTkFrame(col_esq_prof, height=1, fg_color=COR_PROFESSOR).pack(fill="x", padx=12, pady=12)
ctk.CTkLabel(col_esq_prof, text="STARK INDUSTRIES  ·  EDU DIVISION",
             font=("Consolas", 8), text_color=COR_PROFESSOR_DIM).pack(pady=4)

col_dir_prof = ctk.CTkFrame(corpo_prof, fg_color="transparent")
col_dir_prof.pack(side="left", expand=True, fill="both")

lbl_modo_prof = ctk.CTkLabel(col_dir_prof, text="◈  SELECIONA UMA FERRAMENTA  ◈",
                              font=FONTE_HUD, text_color=COR_PROFESSOR)
lbl_modo_prof.pack(pady=(0, 8))

entrada_prof = ctk.CTkEntry(
    col_dir_prof,
    placeholder_text="  Escreve aqui o código, tema ou notas...",
    width=550, height=44,
    font=FONTE_CHAT,
    fg_color=COR_PAINEL,
    border_color=COR_PROFESSOR,
    border_width=2,
    text_color=COR_PROFESSOR,
    placeholder_text_color=COR_PROFESSOR_DIM,
    corner_radius=2
)
entrada_prof.pack(pady=4)
entrada_prof.bind("<Return>", lambda e: executar_ferramenta_professor())

jarvis_botao_premium(col_dir_prof, "[ EXECUTAR ]",
                     executar_ferramenta_professor,
                     width=200, height=42, cor=COR_PROFESSOR).pack(pady=6)

caixa_prof = ctk.CTkTextbox(
    col_dir_prof,
    font=FONTE_CHAT,
    fg_color=COR_PAINEL,
    border_color=COR_PROFESSOR,
    border_width=2,
    text_color=COR_PROFESSOR,
    corner_radius=0,
    scrollbar_button_color=COR_PROFESSOR_DIM
)
caixa_prof.pack(expand=True, fill="both", pady=8)
caixa_prof.tag_config("titulo", foreground=COR_PROFESSOR_GLOW)
caixa_prof.tag_config("erro", foreground=COR_ALERTA)
caixa_prof.tag_config("ok", foreground=COR_VERDE)
caixa_prof.insert("end", "  ◈  JARVIS EDU — SISTEMA PRONTO  ◈\n\n", "titulo")
caixa_prof.insert("end", "  Seleciona uma ferramenta e introduz o conteúdo.\n")


ecra_niveis = ctk.CTkFrame(app, fg_color="transparent")
nivel_escolhido_var = ctk.IntVar(value=1)
label_erro_nivel = None
entrada_pass_nivel = None

def mostrar_ecra_niveis():
    ecra_seguranca.pack_forget()
    nivel_escolhido_var.set(1)
    entrada_pass_nivel.delete(0, "end")
    label_erro_nivel.configure(text="")
    ecra_niveis.pack(expand=True, fill="both")

def confirmar_nivel():
    global NIVEL_ACESSO_ATUAL
    nivel = nivel_escolhido_var.get()
    passwords = {
        1: "acess*re", 2: "acessguest*re", 3: "acessanalyst*re",
        4: "acessoperator*re", 5: "acessadmin*re", 6: "teacher2026"
    }
    if entrada_pass_nivel.get() == passwords[nivel]:
        NIVEL_ACESSO_ATUAL = nivel
        from core.cerebro import definir_nivel
        definir_nivel(nivel)
        label_erro_nivel.configure(text="")
        ecra_niveis.pack_forget()
        atualizar_widgets_nivel()
        adaptar_menu_ao_nivel()
        jarvis_falar(f"Nível {nivel} ativo.")
        ecra_inicial.pack(expand=True, fill="both")
    else:
        label_erro_nivel.configure(text=" PASSWORD INCORRETA")

ctk.CTkLabel(ecra_niveis, text="◈  SELECIONAR NÍVEL DE ACESSO  ◈",
             font=FONTE_TITULO, text_color=COR_PRIMARIA).pack(pady=30)

radio_frame = ctk.CTkFrame(ecra_niveis, fg_color=COR_PAINEL,
                            border_width=2, border_color=COR_BORDA, corner_radius=0)
radio_frame.pack(pady=10, padx=80)

for n in range(1, 7):
    protocolo, role, cor = PROTOCOLOS_ACESSO[n]
    ctk.CTkRadioButton(
        radio_frame,
        text=f"  NÍVEL {n}  —  {role}  |  {protocolo}",
        variable=nivel_escolhido_var,
        value=n,
        font=FONTE_HUD,
        text_color=cor,
        fg_color=cor,
        border_color=cor,
    ).pack(anchor="w", pady=10, padx=30)

ctk.CTkLabel(ecra_niveis, text="PASSWORD DO NÍVEL SELECIONADO",
             font=FONTE_HUD, text_color=COR_SECUNDARIA).pack(pady=(20, 6))

entrada_pass_nivel = ctk.CTkEntry(
    ecra_niveis, show="●", width=300, height=44,
    font=FONTE_HUD, fg_color=COR_PAINEL,
    border_color=COR_BORDA, border_width=2,
    text_color=COR_PRIMARIA, corner_radius=2,
    placeholder_text="PASSWORD DO NÍVEL"
)
entrada_pass_nivel.pack()
entrada_pass_nivel.bind("<Return>", lambda e: confirmar_nivel())

jarvis_botao_premium(ecra_niveis, "[ CONFIRMAR ACESSO ]",
                     confirmar_nivel, width=300, height=46).pack(pady=12)

label_erro_nivel = ctk.CTkLabel(ecra_niveis, text="",
                                 font=FONTE_PEQUENA, text_color=COR_ALERTA)
label_erro_nivel.pack()

try:
    ouvir.iniciar_escuta_continua()
    print("[SISTEMA J.A.R.V.I.S]: Audição de fundo iniciada diretamente pela Interface.")
except Exception as e:
    print(f"[ERRO]: Não foi possível ligar o microfone no arranque: {e}")
ecra_inicial = ctk.CTkFrame(app, fg_color="transparent")

layout_inicial = ctk.CTkFrame(ecra_inicial, fg_color="transparent")
layout_inicial.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)


col_esq = ctk.CTkFrame(layout_inicial, fg_color=COR_PAINEL,
                        border_width=2, border_color=COR_BORDA,
                        width=170, corner_radius=0)
col_esq.pack(side="left", fill="y", padx=(20, 0), pady=20)
col_esq.pack_propagate(False)

ctk.CTkLabel(col_esq, text="◈ STATUS ◈",
             font=FONTE_HUD, text_color=COR_PRIMARIA).pack(pady=12)
for label_t, val_t, cor_t in [
    ("MODO", "OPERACIONAL", COR_VERDE),
    ("IA", "ATIVA", COR_VERDE),
    ("MEMÓRIA", "CARREGADA", COR_VERDE),
    ("VOZ", "PRONTA", COR_PRIMARIA),
    ("REDE", "CONECTADA", COR_PRIMARIA),
]:
    row_e = ctk.CTkFrame(col_esq, fg_color="transparent")
    row_e.pack(anchor="w", padx=16, pady=4)
    ctk.CTkLabel(row_e, text=f"{label_t}: ",
                 font=("Consolas", 10), text_color=COR_TEXTO_DIM).pack(side="left")
    ctk.CTkLabel(row_e, text=val_t,
                 font=("Consolas", 10, "bold"), text_color=cor_t).pack(side="left")

ctk.CTkFrame(col_esq, height=1, fg_color=COR_BORDA).pack(fill="x", padx=12, pady=12)
ctk.CTkLabel(col_esq, text="◈ RADAR ◈",
             font=("Consolas", 9, "bold"), text_color=COR_TEXTO_DIM).pack(pady=(4, 2))
RadarHud(col_esq, size=110).pack(pady=6)
ctk.CTkFrame(col_esq, height=1, fg_color=COR_BORDA).pack(fill="x", padx=12, pady=12)
ctk.CTkLabel(col_esq, text="◈ DADOS ◈",
             font=("Consolas", 9, "bold"), text_color=COR_TEXTO_DIM).pack(pady=(4, 2))
DataMatrix(col_esq, width=146, height=90).pack(pady=4, padx=12)


painel_noticias = ctk.CTkFrame(layout_inicial, fg_color=COR_PAINEL,
                                border_width=2, border_color=COR_BORDA,
                                width=220, corner_radius=0)
painel_noticias.pack(side="left", fill="y", padx=(8, 0), pady=20)
painel_noticias.pack_propagate(False)

ctk.CTkLabel(painel_noticias, text="◈ FEED DE NOTÍCIAS ◈",
             font=("Consolas", 10, "bold"), text_color=COR_PRIMARIA).pack(pady=10)
ctk.CTkFrame(painel_noticias, height=1, fg_color=COR_BORDA).pack(fill="x", padx=8)

noticias_box = ctk.CTkTextbox(
    painel_noticias,
    font=("Consolas", 9),
    fg_color="#020c14",
    border_width=0,
    text_color=COR_VERDE,
    corner_radius=0,
    wrap="word"
)
noticias_box.pack(expand=True, fill="both", padx=6, pady=6)
noticias_box.insert("end", "  A carregar notícias...\n")
noticias_box.configure(state="disabled")

lbl_noticias_update = ctk.CTkLabel(painel_noticias, text="",
                                    font=("Consolas", 7), text_color=COR_TEXTO_DIM)
lbl_noticias_update.pack(pady=(0, 4))


menu_col = ctk.CTkFrame(layout_inicial, fg_color="transparent")
menu_col.pack(side="left", expand=True, fill="both")

menu_inner = ctk.CTkFrame(menu_col, fg_color="transparent")
menu_inner.place(relx=0.5, rely=0.5, anchor="center")

header_menu = ctk.CTkFrame(menu_inner, fg_color="transparent")
header_menu.pack()
for i in range(5):
    w = 70 if i % 2 == 0 else 50
    ctk.CTkFrame(header_menu, width=w, height=2,
                 fg_color=COR_BORDA if i != 2 else COR_PRIMARIA).pack(side="left", padx=3)

ctk.CTkLabel(menu_inner, text="J.A.R.V.I.S",
             font=("Bahnschrift", 48, "bold"), text_color=COR_PRIMARIA).pack(pady=6)
ctk.CTkLabel(menu_inner, text="SISTEMA OPERACIONAL  ·  ACESSO AUTORIZADO",
             font=("Consolas", 11), text_color=COR_SECUNDARIA).pack()

footer_menu = ctk.CTkFrame(menu_inner, fg_color="transparent")
footer_menu.pack(pady=(4, 8))
for i in range(5):
    w = 70 if i % 2 == 0 else 50
    ctk.CTkFrame(footer_menu, width=w, height=2,
                 fg_color=COR_BORDA if i != 2 else COR_PRIMARIA).pack(side="left", padx=3)

nivel_widget_menu = NivelAcessoWidget(menu_inner, width=340)
nivel_widget_menu.pack(pady=(4, 0))
lbl_nivel_menu = ctk.CTkLabel(menu_inner, text="",
                               font=("Consolas", 9), text_color=COR_PRIMARIA)
lbl_nivel_menu.pack(pady=(2, 6))

arc_menu = ArcReactorUltra(menu_inner, size=160)
arc_menu.pack(pady=10)

ctk.CTkLabel(menu_inner, text="SELECIONAR MODO DE INTERFACE",
             font=FONTE_HUD, text_color=COR_SECUNDARIA).pack(pady=(10, 12))

jarvis_botao_premium(menu_inner, "[ MODO CHAT — TEXTO ]",
                     abrir_modo_texto, width=340, height=54).pack(pady=8)
btn_modo_voz = jarvis_botao_premium(menu_inner, "[ MODO JARVIS — VOZ ]",
                                     abrir_modo_voz, width=340, height=54, cor=COR_OURO)
btn_modo_voz.pack(pady=8)
btn_professor = jarvis_botao_premium(menu_inner, "[ MODO PROFESSOR ]",
                                      abrir_modo_professor, width=340, height=54, cor=COR_OURO)

ctk.CTkLabel(menu_inner, text="STARK INDUSTRIES  ·  CONFIDENTIAL  ·  AI DIVISION",
             font=("Consolas", 9), text_color=COR_TEXTO_DIM).pack(pady=(24, 0))


painel_tempo = ctk.CTkFrame(layout_inicial, fg_color=COR_PAINEL,
                             border_width=2, border_color=COR_BORDA,
                             width=220, corner_radius=0)
painel_tempo.pack(side="left", fill="y", padx=(8, 0), pady=20)
painel_tempo.pack_propagate(False)

ctk.CTkLabel(painel_tempo, text="◈ METEOROLOGIA ◈",
             font=("Consolas", 10, "bold"), text_color=COR_OURO).pack(pady=10)
ctk.CTkFrame(painel_tempo, height=1, fg_color=COR_BORDA).pack(fill="x", padx=8)

tempo_box = ctk.CTkTextbox(
    painel_tempo,
    font=("Consolas", 9),
    fg_color="#020c14",
    border_width=0,
    text_color=COR_OURO,
    corner_radius=0,
    wrap="word"
)
tempo_box.pack(expand=True, fill="both", padx=6, pady=6)
tempo_box.insert("end", "  A carregar meteorologia...\n")
tempo_box.configure(state="disabled")

lbl_tempo_update = ctk.CTkLabel(painel_tempo, text="",
                                 font=("Consolas", 7), text_color=COR_TEXTO_DIM)
lbl_tempo_update.pack(pady=(0, 4))


col_dir = ctk.CTkFrame(layout_inicial, fg_color=COR_PAINEL,
                        border_width=2, border_color=COR_BORDA,
                        width=170, corner_radius=0)
col_dir.pack(side="right", fill="y", padx=(0, 20), pady=20)
col_dir.pack_propagate(False)

ctk.CTkLabel(col_dir, text="◈ MISSÃO ◈",
             font=FONTE_HUD, text_color=COR_OURO).pack(pady=12)
for missao in ["ANÁLISE IA", "VOZ ACTIVA", "SEGURANÇA", "TELEMETRIA", "ENCRIPTAÇÃO"]:
    m_row = ctk.CTkFrame(col_dir, fg_color="transparent")
    m_row.pack(anchor="w", padx=16, pady=5)
    ctk.CTkLabel(m_row, text="● ", font=("Arial", 10), text_color=COR_VERDE).pack(side="left")
    ctk.CTkLabel(m_row, text=missao, font=("Consolas", 10, "bold"),
                 text_color=COR_PRIMARIA).pack(side="left")

ctk.CTkFrame(col_dir, height=1, fg_color=COR_BORDA).pack(fill="x", padx=12, pady=12)
ctk.CTkLabel(col_dir, text="◈ LOGS ◈",
             font=("Consolas", 9, "bold"), text_color=COR_TEXTO_DIM).pack(pady=(4, 2))
log_box = ctk.CTkTextbox(col_dir, width=146, height=160,
                          font=("Consolas", 8), fg_color="#020c14",
                          border_color=COR_BORDA, border_width=1,
                          text_color=COR_VERDE, corner_radius=0)
log_box.pack(padx=12, pady=4)
for log in ["[OK] Sistema iniciado", "[OK] IA carregada", "[OK] Voz pronta",
            "[OK] Rede ativa", "[OK] Auth concluída", "[INFO] Aguardando..."]:
    log_box.insert("end", f"{log}\n")
log_box.configure(state="disabled")

ctk.CTkFrame(col_dir, height=1, fg_color=COR_BORDA).pack(fill="x", padx=12, pady=8)
ctk.CTkLabel(col_dir, text="v4.5 ULTRA BUILD",
             font=("Consolas", 8), text_color=COR_TEXTO_DIM).pack(pady=4)


ecra_chat = ctk.CTkFrame(app, fg_color="transparent")

topo_chat = ctk.CTkFrame(ecra_chat, fg_color=COR_PAINEL,
                         corner_radius=0, border_width=2, border_color=COR_BORDA, height=50)
topo_chat.pack(fill="x", padx=24, pady=(20, 0))
topo_chat.pack_propagate(False)

jarvis_botao_premium(topo_chat, "◀ VOLTAR", voltar_menu,
                     width=120, height=36, cor=COR_SECUNDARIA).pack(side="left", padx=12, pady=7)
ctk.CTkLabel(topo_chat, text="◈  INTERFACE DE COMUNICAÇÃO TEXTUAL  ◈",
             font=FONTE_HUD, text_color=COR_PRIMARIA).pack(side="left", padx=24)

nivel_widget_chat = NivelAcessoWidget(topo_chat, width=180)
nivel_widget_chat.pack(side="right", padx=(0, 8), pady=4)

chat_body = ctk.CTkFrame(ecra_chat, fg_color="transparent")
chat_body.pack(expand=True, fill="both", padx=24, pady=(8, 0))

chat_lat = ctk.CTkFrame(chat_body, fg_color=COR_PAINEL,
                         border_width=2, border_color=COR_BORDA,
                         width=180, corner_radius=0)
chat_lat.pack(side="left", fill="y", padx=(0, 12))
chat_lat.pack_propagate(False)

ctk.CTkLabel(chat_lat, text="◈ SESSÃO ◈",
             font=("Consolas", 10, "bold"), text_color=COR_PRIMARIA).pack(pady=10)
for s_lbl, s_val in [("MODELO", "GROQ"), ("LANG", "PT-PT"), ("ENCRIPT", "AES")]:
    s_row = ctk.CTkFrame(chat_lat, fg_color="transparent")
    s_row.pack(anchor="w", padx=10, pady=3)
    ctk.CTkLabel(s_row, text=f"{s_lbl}: ", font=("Consolas", 9),
                 text_color=COR_TEXTO_DIM).pack(side="left")
    ctk.CTkLabel(s_row, text=s_val, font=("Consolas", 9, "bold"),
                 text_color=COR_VERDE).pack(side="left")

ctk.CTkFrame(chat_lat, height=1, fg_color=COR_BORDA).pack(fill="x", padx=8, pady=6)
ctk.CTkLabel(chat_lat, text="◈ ACESSO ◈",
             font=("Consolas", 8), text_color=COR_TEXTO_DIM).pack(pady=2)
lbl_nivel_chat = ctk.CTkLabel(chat_lat, text="",
                               font=("Consolas", 8, "bold"), text_color=COR_PRIMARIA,
                               wraplength=160)
lbl_nivel_chat.pack(padx=8, pady=4)

ctk.CTkFrame(chat_lat, height=1, fg_color=COR_BORDA).pack(fill="x", padx=8, pady=6)
ctk.CTkLabel(chat_lat, text="◈ RADAR ◈",
             font=("Consolas", 8), text_color=COR_TEXTO_DIM).pack(pady=2)
RadarHud(chat_lat, size=100).pack(pady=4)

ctk.CTkFrame(chat_lat, height=1, fg_color=COR_BORDA).pack(fill="x", padx=8, pady=8)
ctk.CTkLabel(chat_lat, text="◈ DADOS ◈",
             font=("Consolas", 8), text_color=COR_TEXTO_DIM).pack(pady=2)
DataMatrix(chat_lat, width=160, height=80).pack(padx=8)

chat_main = ctk.CTkFrame(chat_body, fg_color="transparent")
chat_main.pack(side="left", expand=True, fill="both")

caixa_chat = ctk.CTkTextbox(
    chat_main, width=700, height=500,
    font=FONTE_CHAT,
    fg_color=COR_PAINEL,
    border_color=COR_BORDA,
    border_width=2,
    text_color=COR_PRIMARIA,
    corner_radius=0,
    scrollbar_button_color=COR_BORDA,
    scrollbar_button_hover_color=COR_SECUNDARIA
)
caixa_chat.pack(expand=True, fill="both")
caixa_chat.tag_config("user", foreground=COR_OURO)
caixa_chat.tag_config("jarvis", foreground=COR_PRIMARIA)
caixa_chat.tag_config("alerta", foreground=COR_ALERTA)
caixa_chat.insert("end", "  ◈  SISTEMA JARVIS INICIALIZADO  ◈\n\n", "jarvis")
caixa_chat.insert("end", "  Como posso ajudar, senhor?\n", "jarvis")

zona_inferior_chat = ctk.CTkFrame(ecra_chat, fg_color=COR_PAINEL,
                                  corner_radius=0, border_width=2, border_color=COR_BORDA)
zona_inferior_chat.pack(fill="x", padx=24, pady=(8, 18))

barra_texto = ctk.CTkEntry(
    zona_inferior_chat, width=550, height=42,
    placeholder_text="  INTRODUZA COMANDO...",
    font=FONTE_CHAT,
    fg_color="transparent",
    border_width=0,
    text_color=COR_PRIMARIA,
    placeholder_text_color=COR_TEXTO_DIM,
    corner_radius=0
)
barra_texto.pack(side="left", padx=(12, 0), pady=6)
barra_texto.bind("<Return>", lambda e: enviar_mensagem_texto())

ctk.CTkFrame(zona_inferior_chat, width=2, fg_color=COR_BORDA).pack(side="left", fill="y", pady=8, padx=4)
jarvis_botao_premium(zona_inferior_chat, "ENVIAR ›", enviar_mensagem_texto,
                     width=130, height=42).pack(side="left", padx=10)

ai_ind = ctk.CTkFrame(zona_inferior_chat, fg_color="transparent")
ai_ind.pack(side="right", padx=16)
ctk.CTkLabel(ai_ind, text="●", font=("Arial", 10), text_color=COR_VERDE).pack(side="left", padx=2)
ctk.CTkLabel(ai_ind, text="IA PRONTA", font=("Consolas", 9), text_color=COR_VERDE).pack(side="left")


ecra_voz = ctk.CTkFrame(app, fg_color="transparent")

topo_voz = ctk.CTkFrame(ecra_voz, fg_color=COR_PAINEL,
                        corner_radius=0, border_width=2, border_color=COR_BORDA, height=50)
topo_voz.pack(fill="x", padx=24, pady=(20, 0))
topo_voz.pack_propagate(False)

jarvis_botao_premium(topo_voz, "◀ VOLTAR", voltar_menu,
                     width=120, height=36, cor=COR_SECUNDARIA).pack(side="left", padx=12, pady=7)
ctk.CTkLabel(topo_voz, text="◈  INTERFACE DE COMUNICAÇÃO VOCAL  ◈",
             font=FONTE_HUD, text_color=COR_PRIMARIA).pack(side="left", padx=24)

nivel_widget_voz = NivelAcessoWidget(topo_voz, width=180)
nivel_widget_voz.pack(side="right", padx=(0, 8), pady=4)

voz_layout = ctk.CTkFrame(ecra_voz, fg_color="transparent")
voz_layout.pack(expand=True, fill="both", padx=24, pady=12)

voz_esq = ctk.CTkFrame(voz_layout, fg_color=COR_PAINEL,
                        border_width=2, border_color=COR_BORDA, width=190, corner_radius=0)
voz_esq.pack(side="left", fill="y", padx=(0, 16))
voz_esq.pack_propagate(False)

ctk.CTkLabel(voz_esq, text="◈ AUDIO HUD ◈",
             font=("Consolas", 10, "bold"), text_color=COR_OURO).pack(pady=10)
for a_lbl, a_val in [("CODEC", "PCM 16bit"), ("FREQ", "44.1kHz"),
                      ("CANAIS", "MONO"), ("BUFFER", "512ms"),
                      ("SNR", "42.3 dB"), ("LATÊNCIA", "~120ms")]:
    a_row = ctk.CTkFrame(voz_esq, fg_color="transparent")
    a_row.pack(anchor="w", padx=12, pady=3)
    ctk.CTkLabel(a_row, text=f"{a_lbl}: ", font=("Consolas", 9),
                 text_color=COR_TEXTO_DIM).pack(side="left")
    ctk.CTkLabel(a_row, text=a_val, font=("Consolas", 9, "bold"),
                 text_color=COR_PRIMARIA).pack(side="left")

ctk.CTkFrame(voz_esq, height=1, fg_color=COR_BORDA).pack(fill="x", padx=8, pady=10)
ctk.CTkLabel(voz_esq, text="◈ ACESSO ◈",
             font=("Consolas", 8), text_color=COR_TEXTO_DIM).pack(pady=2)
lbl_nivel_voz = ctk.CTkLabel(voz_esq, text="",
                               font=("Consolas", 8, "bold"), text_color=COR_PRIMARIA,
                               wraplength=170)
lbl_nivel_voz.pack(padx=8, pady=4)

ctk.CTkFrame(voz_esq, height=1, fg_color=COR_BORDA).pack(fill="x", padx=8, pady=6)
ctk.CTkLabel(voz_esq, text="◈ RADAR ◈",
             font=("Consolas", 8), text_color=COR_TEXTO_DIM).pack(pady=2)
RadarHud(voz_esq, size=110).pack(pady=6)

voz_col = ctk.CTkFrame(voz_layout, fg_color="transparent")
voz_col.pack(side="left", expand=True, fill="both")

voz_inner = ctk.CTkFrame(voz_col, fg_color="transparent")
voz_inner.place(relx=0.5, rely=0.5, anchor="center")

arc_voz = ArcReactorUltra(voz_inner, size=200)
arc_voz.pack(pady=(0, 16))

ctk.CTkLabel(voz_inner, text="◈  MODO DE VOZ ATIVO  ◈",
             font=("Bahnschrift", 22, "bold"), text_color=COR_PRIMARIA).pack(pady=6)
ctk.CTkLabel(voz_inner, text='Diga "DESLIGAR" para terminar a sessão',
             font=FONTE_PEQUENA, text_color=COR_SECUNDARIA).pack(pady=4)

ctk.CTkLabel(voz_inner, text="◈  ESPECTRO DE ÁUDIO  ◈",
             font=("Consolas", 9), text_color=COR_TEXTO_DIM).pack(pady=(12, 4))
wave_viz = WaveVisualizer(voz_inner, width=480, height=90)
wave_viz.pack(pady=4)

hud_separator_glow(voz_inner)

jarvis_botao_premium(voz_inner, "[ LIGAR MICROFONE ]",
                     iniciar_escuta_thread, width=320, height=60, cor=COR_OURO).pack(pady=16)

ctk.CTkLabel(voz_inner, text="PROCESSAMENTO DE LINGUAGEM NATURAL  ·  ONLINE",
             font=("Consolas", 9), text_color=COR_TEXTO_DIM).pack(pady=4)

voz_dir = ctk.CTkFrame(voz_layout, fg_color=COR_PAINEL,
                        border_width=2, border_color=COR_BORDA, width=190, corner_radius=0)
voz_dir.pack(side="right", fill="y", padx=(16, 0))
voz_dir.pack_propagate(False)

ctk.CTkLabel(voz_dir, text="◈ NLP STATUS ◈",
             font=("Consolas", 10, "bold"), text_color=COR_PRIMARIA).pack(pady=10)
for n_lbl, n_val, n_col in [
    ("STT", "ATIVO", COR_VERDE),
    ("TTS", "ATIVO", COR_VERDE),
    ("NLU", "PRONTO", COR_PRIMARIA),
    ("INTENT", "AGUARDA", COR_OURO),
    ("RESP", "GERAÇÃO", COR_PRIMARIA),
]:
    n_row = ctk.CTkFrame(voz_dir, fg_color="transparent")
    n_row.pack(anchor="w", padx=12, pady=4)
    ctk.CTkLabel(n_row, text="● ", font=("Arial", 10), text_color=n_col).pack(side="left")
    ctk.CTkLabel(n_row, text=f"{n_lbl}: ", font=("Consolas", 9),
                 text_color=COR_TEXTO_DIM).pack(side="left")
    ctk.CTkLabel(n_row, text=n_val, font=("Consolas", 9, "bold"), text_color=n_col).pack(side="left")

ctk.CTkFrame(voz_dir, height=1, fg_color=COR_BORDA).pack(fill="x", padx=8, pady=10)
ctk.CTkLabel(voz_dir, text="◈ DADOS ◈",
             font=("Consolas", 8), text_color=COR_TEXTO_DIM).pack(pady=2)
DataMatrix(voz_dir, width=166, height=100).pack(padx=12)

ctk.CTkFrame(voz_dir, height=1, fg_color=COR_BORDA).pack(fill="x", padx=8, pady=8)
ctk.CTkLabel(voz_dir, text="◈ LOG VOZ ◈",
             font=("Consolas", 8), text_color=COR_TEXTO_DIM).pack(pady=2)
log_voz = ctk.CTkTextbox(voz_dir, width=166, height=120,
                          font=("Consolas", 8), fg_color="#020c14",
                          border_color=COR_BORDA, border_width=1,
                          text_color=COR_VERDE, corner_radius=0)
log_voz.pack(padx=12, pady=4)
for l in ["[OK] Mic inicializado", "[OK] STT carregado", "[OK] TTS pronto", "[INFO] A aguardar..."]:
    log_voz.insert("end", f"{l}\n")
log_voz.configure(state="disabled")

# ============================================================
app.mainloop()

