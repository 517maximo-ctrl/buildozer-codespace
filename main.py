import os
from kivy.utils import platform
from kivy.core.window import Window

if platform != "android":
    Window.set_icon("Images/AppRunner.png")

Window.title = "Running App by Massimo Moretti"

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from datetime import datetime
import csv
import os

from kivy.lang import Builder

# --- PDF: desktop = ReportLab, Android = Pillow ---
if platform != "android":
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfbase.pdfmetrics import stringWidth
else:
    from PIL import Image, ImageDraw, ImageFont


# ============================================================
#   LETTURA FILE JONES
# ============================================================

from kivy.resources import resource_find
import csv
import os

def load_jones():
    # Trova il file sia su Windows che dentro l'APK Android
    filename = resource_find("Tbl_Program_Training.json")

    if not filename:
        print("ERRORE: File Jones non trovato")
        return []

    table = []
    with open(filename, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            clean = {}
            for k, v in row.items():
                if v is None:
                    v = ""
                v = v.strip()
                v = v.replace("\ufeff", "")
                v = v.replace("\r", "")
                v = v.replace("\n", "")

                if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
                    v = v[1:-1]

                clean[k.strip()] = v
            table.append(clean)

    return table


# ============================================================
#   PARSING RITMO
# ============================================================

def parse_ritmo(txt):
    txt = txt.strip().replace(" ", "")

    if ":" in txt:
        m, s = txt.split(":")
        return int(m) + int(s) / 60

    if "," in txt:
        m, s = txt.split(",")
        return int(m) + int(s) / 60

    if "." in txt:
        m, s = txt.split(".")
        return int(m) + int(s) / 60

    return float(txt)


# ============================================================
#   SCHERMATE
# ============================================================

class LoadingScreen(Screen):
    pass


class ProgrammaScreen(Screen):

    # --------------------------------------------------------
    #   NOME GIORNO
    # --------------------------------------------------------
    def nome_giorno(self, num):
        giorni = {
            1: "Lunedì",
            2: "Martedì",
            3: "Mercoledì",
            4: "Giovedì",
            5: "Venerdì",
            6: "Sabato",
            7: "Domenica",
        }
        return giorni.get(num, "")

    # --------------------------------------------------------
    #   SOSTITUZIONE RITMI (identica al VB6)
    # --------------------------------------------------------
    def sostituisci_ritmi(self, descr, r, ritmo_base, tipo_domenica, giorno):
        r1 = r["RITMO1"].strip()
        r2 = r["RITMO2"].strip()
        r3 = r["RITMO3"].strip()
        r4 = r["RITMO4"].strip()

        def calc(p):
            if not p or p == "0":
                return None
            try:
                p = float(p)
                vel = ritmo_base / (p / 100.0)
                minuti = int(vel)
                secondi = int((vel - minuti) * 60)
                return f"{minuti}:{secondi:02d}"
            except:
                return None

        rr = [calc(r1), calc(r2), calc(r3), calc(r4)]

        out = descr
        for ritmo in rr:
            if ritmo and "X'XX" in out:
                out = out.replace("X'XX", ritmo, 1)

        if giorno == 7:
            if tipo_domenica == "Gara":
                return "GARA"
            if "oppure" in out:
                return out.split("oppure")[0].strip()

        return out

    # --------------------------------------------------------
    #   GENERA PROGRAMMA
    # --------------------------------------------------------
    def genera_programma(self):

        ids = self.ids

        atleta = ids.atleta.text.strip()
        datainizio = ids.datainizio.text.strip()
        datafine = ids.datafine.text.strip()
        corsa = ids.corsa.text.strip()
        ritmo_txt = ids.ritmo.text.strip()
        scala_txt = ids.scala.text.strip()
        tipo_domenica = ids.tipo_domenica.text.strip()

        giorni_selezionati = []
        for i in range(1, 8):
            if ids[f"ch{i}"].active:
                giorni_selezionati.append(str(i))

        errori = []
        if not atleta: errori.append("Inserisci il nome atleta.")
        if not datainizio: errori.append("Inserisci la data di inizio.")
        if not datafine: errori.append("Inserisci la data di fine.")
        if not corsa or "Seleziona" in corsa: errori.append("Seleziona un obiettivo.")
        if not ritmo_txt: errori.append("Inserisci il ritmo base.")
        if not giorni_selezionati: errori.append("Seleziona almeno un giorno di allenamento.")

        if errori:
            ids.output.text = "[b][color=ff0000]" + "\n".join(errori) + "[/color][/b]"
            return

        try:
            d_inizio = datetime.strptime(datainizio, "%Y-%m-%d")
            d_fine = datetime.strptime(datafine, "%Y-%m-%d")
        except:
            ids.output.text = "[b][color=ff0000]Formato data non valido (YYYY-MM-DD).[/color][/b]"
            return

        delta_giorni = (d_fine - d_inizio).days
        if delta_giorni <= 0:
            ids.output.text = "[b][color=ff0000]La data di fine deve essere successiva alla data di inizio.[/color][/b]"
            return

        try:
            ritmo_base = parse_ritmo(ritmo_txt)
        except:
            ids.output.text = "[b][color=ff0000]Ritmo base non valido.[/color][/b]"
            return

        try:
            scala = float(scala_txt.replace(",", "."))
        except:
            scala = 0.0

        ritmo_corretto = ritmo_base * (1 - scala / 100.0)

        week_week = int(delta_giorni / 7)
        txt_giorni = len(giorni_selezionati)
        long_week = int(((delta_giorni / 7.0) * txt_giorni) + 0.7)

        base_tprogram = "0"
        base_long_time = "1"

        if corsa in ("MARATONA", "MEZZA MARATONA"):
            if week_week <= 4:
                base_long_time = "1"; base_tprogram = "1"
            if week_week > 4:
                base_long_time = "2"
            if week_week > 8:
                base_long_time = "3"
            if week_week > 12:
                base_long_time = "4"
            if week_week > 16:
                base_long_time = "5"

        elif corsa == "STRADA 10-14 KM":
            if week_week <= 4:
                base_long_time = "1"; base_tprogram = "1"
            if week_week > 4:
                base_long_time = "2"
            if week_week > 8:
                base_long_time = "3"
            if week_week > 12:
                base_long_time = "4"

        elif corsa in ("CROSS", "CORSA A TAPPE"):
            base_long_time = "1" if week_week <= 4 else "2"

        elif corsa == "PREPARAZIONE BASE":
            base_tprogram = "4"
            base_long_time = "1" if week_week <= 4 else "2"

        elif corsa == "PRIMI PASSI":
            base_tprogram = "5"
            base_long_time = "1"

        elif corsa == "CORSA IN MONTAGNA":
            base_long_time = "1"

        TBL = load_jones()

        righe = [
            r for r in TBL
            if r["TIPOCORSA"] == corsa
            and r["GIORNO"] in giorni_selezionati
            and r["TPROGRAM"] == base_tprogram
            and r["LONGTIME"] == base_long_time
        ]

        righe.sort(key=lambda x: (int(x["SETTIMANA"]), int(x["GIORNO"])))
        righe = righe[:long_week]

        if not righe:
            ids.output.text = (
                "[b]Programma generato (logica ok)[/b]\n\n"
                "Ma il file Jones non contiene righe compatibili."
            )
            return

        lines = []
        lines.append(f"Programma allenamento")
        lines.append(f"Atleta: {atleta}")
        lines.append(f"Ritmo Medio: {ritmo_txt}")
        lines.append(f"Obiettivo: {corsa}")
        lines.append(f"Periodo: {datainizio} - {datafine}")
        lines.append("")

        for r in righe:
            giorno = int(r["GIORNO"])
            settimana = r["SETTIMANA"]
            descr = r["DESCRIZION"]

            descr_finale = self.sostituisci_ritmi(
                descr,
                r,
                ritmo_corretto,
                tipo_domenica,
                giorno
            )

            lines.append(f"Settimana {settimana} - {self.nome_giorno(giorno)}: {descr_finale}")
            lines.append("[color=888888]────────────────────────────────────[/color]")

        lines.append("")
        lines.append("dati elaborati da massimomoretti.it")
        lines.append("Inizia a correre ed in breve tempo la tua salute migliorerà")

        ids.output.text = "\n".join(lines)

        # --------------------------------------------------------
    #   SALVA / APRI PDF (DESKTOP salva, ANDROID apre senza salvare)
    # --------------------------------------------------------
    def salva_pdf(self):

        try:
            output_text = self.ids.output.text
            if not output_text.strip():
                self.ids.output.text = "[b][color=ff0000]Genera prima il programma![/color][/b]"
                return

            # --------------------------------------------------------
            #   DESKTOP → SALVA NORMALMENTE
            # --------------------------------------------------------
            if platform != "android":
                save_path = os.getcwd()
                filename = os.path.join(save_path, "programma_allenamento.pdf")

                c = canvas.Canvas(filename, pagesize=A4)
                larghezza, altezza = A4
                y = altezza - 3*cm

                try:
                    c.drawImage("Images/AppRunner.png", 2*cm, y-2*cm, width=3*cm, height=3*cm)
                except:
                    pass

                c.setFont("Helvetica-Bold", 16)
                c.drawString(6*cm, y-1*cm, "Programma Allenamento")
                y -= 2.5*cm

                c.setFont("Helvetica", 11)
                max_width = larghezza - 4*cm

                def draw_wrapped(text, y):
                    lines = []
                    for raw_line in text.split("\n"):
                        line = raw_line.strip()

                        if not line:
                            lines.append("")
                            continue

                        if "────" in line:
                            lines.append("LINEA_PDF")
                            continue

                        current = ""
                        for word in line.split(" "):
                            test = current + (" " if current else "") + word
                            if stringWidth(test, "Helvetica", 11) < max_width:
                                current = test
                            else:
                                lines.append(current)
                                current = word
                        lines.append(current)

                    for line in lines:
                        if y < 2*cm:
                            c.showPage()
                            c.setFont("Helvetica", 11)
                            y = altezza - 2*cm

                        if line == "LINEA_PDF":
                            c.line(2*cm, y, larghezza - 2*cm, y)
                            y -= 0.45*cm
                            continue

                        c.drawString(2*cm, y, line)
                        y -= 0.55*cm

                    return y

                y = draw_wrapped(output_text, y)

                c.setFont("Helvetica-Oblique", 10)
                c.drawString(2*cm, 1.5*cm, "dati elaborati da massimomoretti.it")
                c.save()

                self.ids.output.text += f"\n\n[b]PDF salvato in:[/b]\n{filename}"
                self.last_pdf_path = filename
                return

            # --------------------------------------------------------
            #   ANDROID → CREA PDF TEMPORANEO E APRILO
            # --------------------------------------------------------
            else:
                from jnius import autoclass
                from PIL import Image, ImageDraw, ImageFont

                W, H = 1240, 1754
                MARGIN = 80
                LINE_HEIGHT = 42

                try:
                    font = ImageFont.truetype("/system/fonts/Roboto-Regular.ttf", 32)
                except:
                    font = ImageFont.load_default()

                pages = []
                img = Image.new("RGB", (W, H), "white")
                draw = ImageDraw.Draw(img)
                y = MARGIN

                for line in output_text.split("\n"):

                    clean = (
                        line.replace("[color=888888]", "")
                            .replace("[/color]", "")
                            .replace("[b]", "")
                            .replace("[/b]", "")
                    )

                    if "────" in clean:
                        draw.line((MARGIN, y, W - MARGIN, y), fill=(150,150,150), width=3)
                        y += LINE_HEIGHT
                        continue

                    if y > H - MARGIN:
                        pages.append(img)
                        img = Image.new("RGB", (W, H), "white")
                        draw = ImageDraw.Draw(img)
                        y = MARGIN

                    draw.text((MARGIN, y), clean, fill="black", font=font)
                    y += LINE_HEIGHT

                pages.append(img)

                # FILE TEMPORANEO
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                context = PythonActivity.mActivity
                temp_path = context.getCacheDir().getAbsolutePath() + "/programma_temp.pdf"

                pages[0].save(
                    temp_path,
                    "PDF",
                    resolution=150.0,
                    save_all=True,
                    append_images=pages[1:]
                )

                # APRI SUBITO IL PDF
                Intent = autoclass('android.content.Intent')
                File = autoclass('java.io.File')
                FileProvider = autoclass('androidx.core.content.FileProvider')

                file_obj = File(temp_path)
                uri = FileProvider.getUriForFile(
                    context,
                    "it.massimomoretti.app.runningapp.fileprovider",
                    file_obj
                )

                intent = Intent(Intent.ACTION_VIEW)
                intent.setDataAndType(uri, "application/pdf")
                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)

                try:
                    context.startActivity(intent)
                except:
                    self.ids.output.text = "[b][color=ff0000]Nessuna app PDF disponibile![/color][/b]"

                self.last_pdf_path = temp_path
                self.ids.output.text += "\n\n[b]PDF aperto (non salvato).[/b]"

        except Exception as e:
            import traceback
            err = traceback.format_exc()
            self.ids.output.text += (
                f"\n\n[b][color=ff0000]Errore in salva_pdf:[/color][/b]\n{e}\n{err}"
            )


    # --------------------------------------------------------
    #   APRI PDF (riapre il PDF temporaneo)
    # --------------------------------------------------------
    def apri_pdf(self):

        if not hasattr(self, "last_pdf_path"):
            self.ids.output.text = "[b][color=ff0000]Nessun PDF da aprire![/color][/b]"
            return

        filename = self.last_pdf_path

        if platform == "android":
            from jnius import autoclass

            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity
            Intent = autoclass('android.content.Intent')
            File = autoclass('java.io.File')
            FileProvider = autoclass('androidx.core.content.FileProvider')

            file_obj = File(filename)
            uri = FileProvider.getUriForFile(
                context,
                "it.massimomoretti.app.runningapp.fileprovider",
                file_obj
            )

            intent = Intent(Intent.ACTION_VIEW)
            intent.setDataAndType(uri, "application/pdf")
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)

            try:
                context.startActivity(intent)
            except:
                self.ids.output.text = "[b][color=ff0000]Nessuna app PDF disponibile![/color][/b]"

        else:
            import subprocess
            subprocess.Popen(["xdg-open", filename])


    # --------------------------------------------------------
    #   CONDIVIDI PDF (usa il PDF temporaneo)
    # --------------------------------------------------------
    def condividi_pdf(self):

        if not hasattr(self, "last_pdf_path"):
            self.ids.output.text = "[b][color=ff0000]Nessun PDF da condividere![/color][/b]"
            return

        filename = self.last_pdf_path

        if platform == "android":
            from jnius import autoclass

            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity
            Intent = autoclass('android.content.Intent')
            File = autoclass('java.io.File')
            FileProvider = autoclass('androidx.core.content.FileProvider')

            file_obj = File(filename)
            uri = FileProvider.getUriForFile(
                context,
                "it.massimomoretti.app.runningapp.fileprovider",
                file_obj
            )

            intent = Intent(Intent.ACTION_SEND)
            intent.setType("application/pdf")
            intent.putExtra(Intent.EXTRA_STREAM, uri)
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)

            chooser = Intent.createChooser(intent, "Condividi PDF")
            context.startActivity(chooser)

        else:
            self.ids.output.text = "[b]Condivisione disponibile solo su Android[/b]"


# ============================================================
#   TEST DI COOPER (INVARIATO)
# ============================================================

class CooperScreen(Screen):

    def update_distances(self, age, sex):
        table = {
            "Fino a 30|Maschile": ["fino a 1600","1600-2000","2000-2400","2400-2800","oltre 2800"],
            "Fino a 30|Femminile": ["fino a 1550","1550-1850","1850-2150","2170-2650","oltre 2650"],
            "30-39|Maschile": ["fino a 1550","1550-1850","1850-2250","2250-2650","oltre 2650"],
            "30-39|Femminile": ["fino a 1350","1350-1650","1700-2000","2000-2500","oltre 2500"],
            "40-49|Maschile": ["fino a 1350","1350-1650","1700-2100","2100-2500","oltre 2500"],
            "40-49|Femminile": ["fino a 1200","1300-1600","1550-1850","1850-2300","oltre 2350"],
            "50+|Maschile": ["fino a 1200","1300-1600","1600-2100","2100-2400","oltre 2400"],
            "50+|Femminile": ["fino a 1100","1100-1350","1350-1650","1700-2150","oltre 2150"],
        }
        key = f"{age}|{sex}"
        distances = table.get(key, [])
        self.ids.distance_spinner.values = distances
        self.ids.distance_spinner.text = "Seleziona distanza"

    def on_age_change(self, spinner, value):
        sex = self.ids.sex_spinner.text
        if "Seleziona" not in sex:
            self.update_distances(value, sex)

    def on_sex_change(self, spinner, value):
        age = self.ids.age_spinner.text
        if "Seleziona" not in age:
            self.update_distances(age, value)

    def calculate_result(self):
        nome = self.ids.nome.text.strip()
        age = self.ids.age_spinner.text
        sex = self.ids.sex_spinner.text
        dist = self.ids.distance_spinner.text

        if not nome or "Seleziona" in age or "Seleziona" in sex or "Seleziona" in dist:
            self.ids.result_label.text = "Errore: inserisci tutti i dati!"
            return

        cooper_table = {
            "Fino a 30|Maschile": ["Scarso","Sufficiente","Discreto","Buono","Ottimo"],
            "Fino a 30|Femminile": ["Scarso","Sufficiente","Discreto","Buono","Ottimo"],
            "30-39|Maschile": ["Scarso","Sufficiente","Discreto","Buono","Ottimo"],
            "30-39|Femminile": ["Scarso","Sufficiente","Discreto","Buono","Ottimo"],
            "40-49|Maschile": ["Scarso","Sufficiente","Discreto","Buono","Ottimo"],
            "40-49|Femminile": ["Scarso","Sufficiente","Discreto","Buono","Ottimo"],
            "50+|Maschile": ["Scarso","Sufficiente","Discreto","Buono","Ottimo"],
            "50+|Femminile": ["Scarso","Sufficiente","Discreto","Buono","Ottimo"],
        }

        index = self.ids.distance_spinner.values.index(dist)
        giudizio = cooper_table[f"{age}|{sex}"][index]

        self.ids.result_label.text = (
            f"[b]🏃 Test di Cooper – Risultato 🏃[/b]\n\n"
            f"Nome: {nome}\n"
            f"Età: {age}\n"
            f"Sesso: {sex}\n"
            f"Distanza: {dist}\n"
            f"Valutazione: {giudizio}\n\n"
            f"[ref=site][color=#3366cc]dati elaborati da massimomoretti.it[/color][/ref]"
        )


# ============================================================
#   APP
# ============================================================

class RunningApp(App):

    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoadingScreen(name="loading"))
        sm.add_widget(ProgrammaScreen(name="programma"))
        sm.add_widget(CooperScreen(name="cooper"))
        Clock.schedule_once(lambda dt: setattr(sm, "current", "programma"), 1.5)
        return sm

    def on_ref_press(self, instance, value):
        import webbrowser
        webbrowser.open("https://www.massimomoretti.it")


if __name__ == "__main__":
    RunningApp().run()
