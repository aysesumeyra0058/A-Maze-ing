"""
Konfigürasyon Okuyucu Modülü (ConfigParser)
Bu modül, dışarıdan gelen config.txt dosyasını satır satır okur, 
yorum satırlarını temizler, anahtar-değer (KEY=VALUE) eşleşmelerini 
doğrular ve çıktı dosyası yazma işlemlerini yönetir[cite: 22].
"""

import os
from typing import Any, Dict, List, Tuple


class ConfigParser:
    """
    Konfigürasyon dosyasını çözümleyen (parse eden) ve 
    girilen parametrelerin geçerliliğini denetleyen sınıf.
    """

    def __init__(self, filepath: str) -> None:
        """Konfigürasyon dosyasının yolunu ve boş ayar sözlüğünü hazırlar."""
        self.filepath: str = filepath
        self.settings: Dict[str, Any] = {}

    def parse(self) -> Dict[str, Any]:
        """
        Dosyayı satır satır okur; '#' ile başlayan yorumları ve boşlukları temizler.
        Format hatalarında veya dosya bulunamadığında açıklayıcı hatalar fırlatır[cite: 22].
        """
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Konfigürasyon dosyası bulunamadı: {self.filepath}")

        with open(self.filepath, "r", encoding="utf-8") as file_obj:
            for line_no, raw_line in enumerate(file_obj, 1):
                clean_line = raw_line.split("#")[0].strip()
                if not clean_line:
                    continue
                
                if "=" not in clean_line:
                    raise ValueError(
                        f"Satır {line_no} geçersiz formatta (KEY=VALUE bekleniyor): {clean_line}"
                    )
                
                key_part, val_part = clean_line.split("=", 1)
                self._process_kv(key_part.strip(), val_part.strip())

        self._validate()
        return self.settings

    def _process_kv(self, key: str, value: str) -> None:
        """Okunan metin değerlerini uygun veri tiplerine (int, bool, tuple) dönüştürür."""
        if key in ("WIDTH", "HEIGHT"):
            self.settings[key] = int(value)
        elif key in ("ENTRY", "EXIT"):
            coords = value.split(",")
            if len(coords) != 2:
                raise ValueError(f"{key} koordinatları 'x,y' formatında olmalıdır, gelen: {value}")
            self.settings[key] = (int(coords[0].strip()), int(coords[1].strip()))
        elif key == "PERFECT":
            val_lower = value.lower()
            if val_lower in ("true", "1", "yes"):
                self.settings[key] = True
            elif val_lower in ("false", "0", "no"):
                self.settings[key] = False
            else:
                raise ValueError(f"PERFECT değeri boolean (True/False) olmalıdır, gelen: {value}")
        elif key == "SEED":
            if not value or value.lower() == "none":
                self.settings[key] = None
            else:
                self.settings[key] = int(value)
        else:
            self.settings[key] = value

    def _validate(self) -> None:
        """Zorunlu alanların mevcudiyetini ve mantıksal sınır uyumlarını kontrol eder."""
        required_keys = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
        for req in required_keys:
            if req not in self.settings:
                raise ValueError(f"Eksik zorunlu konfigürasyon anahtarı: {req}")

        if self.settings["WIDTH"] <= 0 or self.settings["HEIGHT"] <= 0:
            raise ValueError("WIDTH ve HEIGHT değerleri pozitif tam sayı olmalıdır.")

        max_w = self.settings["WIDTH"]
        max_h = self.settings["HEIGHT"]

        for coord_key in ("ENTRY", "EXIT"):
            px, py = self.settings[coord_key]
            if not (0 <= px < max_w and 0 <= py < max_h):
                raise ValueError(f"{coord_key} koordinatları ({px},{py}) labirent sınırları dışında!")

        if self.settings["ENTRY"] == self.settings["EXIT"]:
            raise ValueError("ENTRY (Giriş) ve EXIT (Çıkış) noktaları aynı hücre olamaz.")

        self.settings.setdefault("SEED", None)

    @staticmethod
    def write_maze_output(
        filepath: str,
        grid_walls: List[List[int]],
        entry_pos: Tuple[int, int],
        exit_pos: Tuple[int, int],
        solution_path: str = "",
    ) -> None:
        """
        Labirentin bit matrisini heksadesimal (hex) karakterler halinde satır satır yazar.
        Ardından boş bir satır bırakarak giriş, çıkış ve çözüm harflerini (N/E/S/W) ekler[cite: 10, 22].
        """
        with open(filepath, "w", encoding="utf-8") as out_file:
            for row in grid_walls:
                hex_row_str = "".join(format(cell_val & 0xF, "x") for cell_val in row)
                out_file.write(hex_row_str + "\n")

            out_file.write("\n")
            out_file.write(f"{entry_pos[0]},{entry_pos[1]}\n")
            out_file.write(f"{exit_pos[0]},{exit_pos[1]}\n")
            out_file.write(f"{solution_path}\n")