#!/usr/bin/env python3
import json
import argparse
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import BooleanObject, NameObject, TextStringObject

def get_nested_value(obj, path):
    """
    Safely walk dicts and lists via dot-notation; return "" on any failure.
    """
    current = obj
    for segment in path.split("."):
        if isinstance(current, dict):
            current = current.get(segment, "")
        elif isinstance(current, list):
            try:
                current = current[int(segment)]
            except (ValueError, IndexError):
                return ""
        else:
            return ""
    return "" if current is None else current

def parse_args():
    p = argparse.ArgumentParser(
        description="Fill a PDF form from JSON and flatten for sharing."
    )
    p.add_argument("input_pdf",  help="path to the blank fillable PDF")
    p.add_argument("json_file",  help="path to the JSON data file")
    p.add_argument("output_pdf", help="path to write the flattened, filled PDF")
    return p.parse_args()

def main():
    args = parse_args()
    data = json.loads(Path(args.json_file).read_text())
    
    field_map = {
        "character.name": "Textfield3761",                     # 001
        "character.xp_earned": "Copy of Textfield3761",        # 002
        "character.xp_to_next": "Copy of Textfield3761 (2)",   # 003
        "character.origin": "Copy of Textfield3761 (3)",       # 004
        "character.level": "Copy of Textfield3761 (4)",        # 005
        "special.L": "Copy of Textfield3761 (5)",              # 006
        "special.A": "Copy of Textfield3761 (6)",              # 007
        "special.S": "Copy of Textfield3761 (7)",              # 008
        "special.I": "Copy of Textfield3761 (8)",              # 009
        "special.C": "Copy of Textfield3761 (9)",              # 010
        "special.E": "Copy of Textfield3761 (10)",             # 011
        "special.P": "Copy of Textfield3761 (11)",             # 012
        "derived.luck_points": "Copy of Textfield3761 (12)",   # 013
        "derived.melee_damage": "Copy of Textfield3761 (13)",  # 014
        "derived.initiative": "Copy of Textfield3761 (14)",    # 015
        "derived.defense": "Copy of Textfield3761 (15)",       # 016
        "resistance.poison_dr": "Copy of Textfield3761 (16)",  # 017
        "resistance.head.rad_dr": "Copy of Textfield3761 (17)",# 018
        "resistance.head.hp": "Copy of Textfield3761 (18)",    # 019
        "resistance.head.phys_dr": "Copy of Textfield3761 (19)",# 020
        "health.torso": "Copy of Textfield3761 (20)",          # 021
        "health.max": "Copy of Textfield3761 (21)",            # 022
        "health.current": "Copy of Textfield3761 (22)",        # 023
        "health.duplicate_current": "Copy of Textfield3761 (23)",#024
        "resistance.left_arm.hp": "Copy of Textfield3761 (24)",# 025
        "resistance.left_leg.hp": "Copy of Textfield3761 (25)",# 026
        "skills.unarmed.rank": "Copy of Textfield3761 (26)",   # 027
        "resistance.right_arm.en_dr": "Copy of Textfield3761 (27)",#028
        "resistance.left_arm.rad_dr": "Copy of Textfield3761 (28)",#029
        "resistance.right_arm.phys_dr": "Copy of Textfield3761 (29)",#030
        "resistance.right_arm.hp": "Copy of Textfield3761 (30)",# 031
        "resistance.right_arm.rad_dr": "Copy of Textfield3761 (31)",#032
        "resistance.head.en_dr": "Copy of Textfield3761 (32)", # 033
        "resistance.torso.en_dr": "Copy of Textfield3761 (33)",# 034
        "resistance.torso.phys_dr": "Copy of Textfield3761 (34)",#035
        "resistance.torso.rad_dr": "Copy of Textfield3761 (35)",#036
        "resistance.left_arm.en_dr": "Copy of Textfield3761 (36)",#037
        "resistance.left_leg.en_dr": "Copy of Textfield3761 (37)",#038
        "resistance.left_leg.phys_dr": "Copy of Textfield3761 (38)",#039
        "resistance.right_leg.hp": "Copy of Textfield3761 (39)",# 040
        "resistance.left_leg.rad_dr": "Copy of Textfield3761 (40)",#041
        "resistance.right_leg.en_dr": "Copy of Textfield3761 (41)",#042
        "resistance.right_leg.phys_dr": "Copy of Textfield3761 (42)",#043
        "resistance.right_leg.rad_dr": "Copy of Textfield3761 (43)",#044
        "resistance.left_arm.phys_dr": "Copy of Textfield3761 (44)",#045
        "skills.athletics.rank": "Copy of Textfield3761 (45)", # 046
        "skills.barter.rank": "Copy of Textfield3761 (46)",    # 047
        "skills.big_guns.rank": "Copy of Textfield3761 (47)",  # 048
        "skills.energy_weapons.rank": "Copy of Textfield3761 (48)",#049
        "skills.explosives.rank": "Copy of Textfield3761 (49)",# 050
        "skills.lockpick.rank": "Copy of Textfield3761 (50)",  # 051
        "skills.medicine.rank": "Copy of Textfield3761 (51)",  # 052
        "skills.melee_weapons.rank": "Copy of Textfield3761 (52)",#053
        "skills.pilot.rank": "Copy of Textfield3761 (53)",     # 054
        "skills.repair.rank": "Copy of Textfield3761 (54)",    # 055
        "skills.science.rank": "Copy of Textfield3761 (55)",   # 056
        "skills.small_guns.rank": "Copy of Textfield3761 (56)",# 057
        "skills.sneak.rank": "Copy of Textfield3761 (57)",     # 058
        "skills.speech.rank": "Copy of Textfield3761 (58)",    # 059
        "skills.survival.rank": "Copy of Textfield3761 (59)",  # 060
        "skills.throwing.rank": "Copy of Textfield3761 (60)",  # 061
        "skills.athletics.tag": "Copy of Checkbox3822",        # 062
        "skills.barter.tag": "Copy of Checkbox3822 (2)",       # 063
        "skills.big_guns.tag": "Copy of Checkbox3822 (3)",     # 064
        "skills.energy_weapons.tag": "Copy of Checkbox3822 (4)",#065
        "skills.explosives.tag": "Copy of Checkbox3822 (5)",   # 066
        "skills.lockpick.tag": "Copy of Checkbox3822 (6)",     # 067
        "skills.medicine.tag": "Copy of Checkbox3822 (7)",     # 068
        "skills.melee_weapons.tag": "Copy of Checkbox3822 (8)",# 069
        "skills.pilot.tag": "Copy of Checkbox3822 (9)",        # 070
        "skills.repair.tag": "Copy of Checkbox3822 (10)",      # 071
        "skills.science.tag": "Copy of Checkbox3822 (11)",     # 072
        "skills.small_guns.tag": "Copy of Checkbox3822 (12)",  # 073
        "skills.sneak.tag": "Copy of Checkbox3822 (13)",       # 074
        "skills.speech.tag": "Copy of Checkbox3822 (14)",      # 075
        "skills.survival.tag": "Copy of Checkbox3822 (15)",    # 076
        "skills.throwing.tag": "Copy of Checkbox3822 (16)",    # 077
        "skills.unarmed.tag": "Copy of Checkbox3822 (17)",     # 078
        "weapons.0.weight": "Copy of Textfield3761 (63)",      # 079
        "weapons.1.name": "Copy of Textfield3761 (64)",        # 080
        "weapons.1.skill": "Copy of Textfield3761 (65)",       # 081
        "weapons.0.damage": "Copy of Textfield3761 (66)",      # 082
        "weapons.0.effects": "Copy of Textfield3761 (67)",     # 083
        "weapons.0.type": "Copy of Textfield3761 (68)",        # 084
        "weapons.0.rate": "Copy of Textfield3761 (69)",        # 085
        "weapons.0.range": "Copy of Textfield3761 (70)",       # 086
        "weapons.0.qualities": "Copy of Textfield3761 (71)",   # 087
        "weapons.0.ammo": "Copy of Textfield3761 (72)",        # 088
        "weapons.0.tn": "Copy of Textfield3761 (73)",          # 089
        "weapons.0.tag": "Copy of Checkbox3822 (18)",          # 090
        "weapons.1.tag": "Copy of Checkbox3822 (19)",          # 091
        "weapons.1.weight": "Copy of Textfield3761 (74)",      # 092
        "weapons.0.name": "Copy of Textfield3761 (75)",        # 093
        "weapons.0.skill": "Copy of Textfield3761 (76)",       # 094
        "weapons.1.damage": "Copy of Textfield3761 (77)",      # 095
        "weapons.1.effects": "Copy of Textfield3761 (78)",     # 096
        "weapons.1.type": "Copy of Textfield3761 (79)",        # 097
        "weapons.1.rate": "Copy of Textfield3761 (80)",        # 098
        "weapons.1.range": "Copy of Textfield3761 (81)",       # 099
        "weapons.1.qualities": "Copy of Textfield3761 (82)",   # 100
        "weapons.1.ammo": "Copy of Textfield3761 (83)",        # 101
        "weapons.1.tn": "Copy of Textfield3761 (84)",          # 102
        "weapons.2.name": "Copy of Textfield3761 (85)",        # 103
        "weapons.2.skill": "Copy of Textfield3761 (86)",       # 104
        "weapons.2.tag": "Copy of Checkbox3822 (20)",          # 105
        "weapons.2.weight": "Copy of Textfield3761 (87)",      # 106
        "weapons.2.damage": "Copy of Textfield3761 (88)",      # 107
        "weapons.2.effects": "Copy of Textfield3761 (89)",     # 108
        "weapons.2.type": "Copy of Textfield3761 (90)",        # 109
        "weapons.2.rate": "Copy of Textfield3761 (91)",        # 110
        "weapons.2.range": "Copy of Textfield3761 (92)",       # 111
        "weapons.2.qualities": "Copy of Textfield3761 (93)",   # 112
        "weapons.2.ammo": "Copy of Textfield3761 (94)",        # 113
        "weapons.2.tn": "Copy of Textfield3761 (95)",          # 114
        "weapons.3.name": "Copy of Textfield3761 (96)",        # 115
        "weapons.3.skill": "Copy of Textfield3761 (97)",       # 116
        "weapons.3.tag": "Copy of Checkbox3822 (21)",          # 117
        "weapons.3.weight": "Copy of Textfield3761 (98)",      # 118
        "weapons.3.damage": "Copy of Textfield3761 (99)",      # 119
        "weapons.3.effects": "Copy of Textfield3761 (100)",    # 120
        "weapons.3.type": "Copy of Textfield3761 (101)",       # 121
        "weapons.3.rate": "Copy of Textfield3761 (102)",       # 122
        "weapons.3.range": "Copy of Textfield3761 (103)",      # 123
        "weapons.3.qualities": "Copy of Textfield3761 (104)",  # 124
        "weapons.3.ammo": "Copy of Textfield3761 (105)",       # 125
        "weapons.3.tn": "Copy of Textfield3761 (106)",         # 126
        "weapons.4.name": "Copy of Textfield3761 (107)",       # 127
        "weapons.4.skill": "Copy of Textfield3761 (108)",      # 128
        "weapons.4.tag": "Copy of Checkbox3822 (22)",          # 129
        "weapons.4.weight": "Copy of Textfield3761 (109)",     # 130
        "weapons.4.damage": "Copy of Textfield3761 (110)",     # 131
        "weapons.4.effects": "Copy of Textfield3761 (111)",    # 132
        "weapons.4.type": "Copy of Textfield3761 (112)",       # 133
        "weapons.4.rate": "Copy of Textfield3761 (113)",       # 134
        "weapons.4.range": "Copy of Textfield3761 (114)",      # 135
        "weapons.4.qualities": "Copy of Textfield3761 (115)",  # 136
        "weapons.4.ammo": "Copy of Textfield3761 (116)",       # 137
        "weapons.4.tn": "Copy of Textfield3761 (117)",         # 138
        "ammo.0.caliber": "Copy of Textfield3761 (62)",        # 139
        "ammo.0.quantity": "Copy of Textfield3761 (118)",      # 140
        "ammo.1.caliber": "Copy of Textfield3761 (119)",       # 141
        "ammo.1.quantity": "Copy of Textfield3761 (120)",      # 142
        "ammo.2.caliber": "Copy of Textfield3761 (121)",       # 143
        "ammo.2.quantity": "Copy of Textfield3761 (122)",      # 144
        "ammo.3.caliber": "Copy of Textfield3761 (123)",       # 145
        "ammo.3.quantity": "Copy of Textfield3761 (124)",      # 146
        "ammo.4.caliber": "Copy of Textfield3761 (125)",       # 147
        "ammo.4.quantity": "Copy of Textfield3761 (126)",      # 148
        "ammo.5.caliber": "Copy of Textfield3761 (127)",       # 149
        "ammo.5.quantity": "Copy of Textfield3761 (128)",      # 150
        "ammo.6.caliber": "Copy of Textfield3761 (129)",       # 151
        "ammo.6.quantity": "Copy of Textfield3761 (130)",      # 152
        "ammo.7.caliber": "Copy of Textfield3761 (131)",       # 153
        "ammo.7.quantity": "Copy of Textfield3761 (132)",      # 154
        "ammo.8.caliber": "Copy of Textfield3761 (133)",       # 155
        "ammo.8.quantity": "Copy of Textfield3761 (134)",      # 156
        "ammo.9.caliber": "Copy of Textfield3761 (135)",       # 157
        "ammo.9.quantity": "Copy of Textfield3761 (136)",      # 158
        "gear.0.item": "Copy of Textfield3761 (137)",          # 159
        "gear.0.weight": "Copy of Textfield3761 (138)",        # 160
        "gear.1.item": "Copy of Textfield3761 (139)",          # 161
        "gear.1.weight": "Copy of Textfield3761 (140)",        # 162
        "gear.2.item": "Copy of Textfield3761 (141)",          # 163
        "gear.2.weight": "Copy of Textfield3761 (142)",        # 164
        "gear.3.item": "Copy of Textfield3761 (143)",          # 165
        "gear.3.weight": "Copy of Textfield3761 (144)",        # 166
        "gear.4.item": "Copy of Textfield3761 (145)",          # 167
        "gear.4.weight": "Copy of Textfield3761 (146)",        # 168
        "gear.5.item": "Copy of Textfield3761 (147)",          # 169
        "gear.5.weight": "Copy of Textfield3761 (148)",        # 170
        "gear.6.item": "Copy of Textfield3761 (149)",          # 171
        "gear.6.weight": "Copy of Textfield3761 (150)",        # 172
        "gear.7.item": "Copy of Textfield3761 (151)",          # 173
        "gear.7.weight": "Copy of Textfield3761 (152)",        # 174
        "gear.8.item": "Copy of Textfield3761 (153)",          # 175
        "gear.8.weight": "Copy of Textfield3761 (154)",        # 176
        "gear.9.item": "Copy of Textfield3761 (155)",          # 177
        "gear.9.weight": "Copy of Textfield3761 (156)",        # 178
        "gear.10.item": "Copy of Textfield3761 (157)",         # 179
        "gear.10.weight": "Copy of Textfield3761 (158)",       # 180
        "gear.11.item": "Copy of Textfield3761 (159)",         # 181
        "gear.11.weight": "Copy of Textfield3761 (160)",       # 182
        "gear.12.item": "Copy of Textfield3761 (161)",         # 183
        "gear.12.weight": "Copy of Textfield3761 (162)",       # 184
        "gear.13.item": "Copy of Textfield3761 (163)",         # 185
        "gear.13.weight": "Copy of Textfield3761 (164)",       # 186
        "gear.14.item": "Copy of Textfield3761 (165)",         # 187
        "gear.14.weight": "Copy of Textfield3761 (166)",       # 188
        "gear.15.item": "Copy of Textfield3761 (167)",         # 189
        "gear.15.weight": "Copy of Textfield3761 (168)",       # 190
        "gear.16.item": "Copy of Textfield3761 (169)",         # 191
        "gear.16.weight": "Copy of Textfield3761 (170)",       # 192
        "gear.17.item": "Copy of Textfield3761 (171)",         # 193
        "gear.17.weight": "Copy of Textfield3761 (172)",       # 194
        "gear.18.item": "Copy of Textfield3761 (173)",         # 195
        "gear.18.weight": "Copy of Textfield3761 (174)",       # 196
        "gear.19.item": "Copy of Textfield3761 (175)",         # 197
        "gear.19.weight": "Copy of Textfield3761 (176)",       # 198
        "carry_weight.current": "Copy of Textfield3761 (177)", # 199
        "carry_weight.maximum": "Copy of Textfield3761 (178)", # 200
        "character.caps": "Copy of Textfield3761 (61)",        # 201
        "perks_traits.0.effect": "Copy of Textfield3761 (179)",# 202
        "perks_traits.0.name": "Copy of Textfield3761 (180)",  # 203
        "perks_traits.0.rank": "Copy of Textfield3761 (181)",  # 204
        "perks_traits.1.effect": "Copy of Textfield3761 (182)",# 205
        "perks_traits.1.name": "Copy of Textfield3761 (183)",  # 206
        "perks_traits.1.rank": "Copy of Textfield3761 (184)",  # 207
        "perks_traits.2.effect": "Copy of Textfield3761 (185)",# 208
        "perks_traits.2.name": "Copy of Textfield3761 (186)",  # 209
        "perks_traits.2.rank": "Copy of Textfield3761 (187)",  # 210
        "perks_traits.3.effect": "Copy of Textfield3761 (188)",# 211
        "perks_traits.3.name": "Copy of Textfield3761 (189)",  # 212
        "perks_traits.3.rank": "Copy of Textfield3761 (190)",  # 213
        "perks_traits.4.effect": "Copy of Textfield3761 (191)",# 214
        "perks_traits.4.name": "Copy of Textfield3761 (192)",  # 215
        "perks_traits.4.rank": "Copy of Textfield3761 (193)",  # 216
        "perks_traits.5.effect": "Copy of Textfield3761 (194)",# 217
        "perks_traits.5.name": "Copy of Textfield3761 (195)",  # 218
        "perks_traits.5.rank": "Copy of Textfield3761 (196)",  # 219
        "perks_traits.6.effect": "Copy of Textfield3761 (197)",# 220
        "perks_traits.6.name": "Copy of Textfield3761 (198)",  # 221
        "perks_traits.6.rank": "Copy of Textfield3761 (199)",  # 222
        "perks_traits.7.effect": "Copy of Textfield3761 (200)",# 223
        "perks_traits.7.name": "Copy of Textfield3761 (201)",  # 224
        "perks_traits.7.rank": "Copy of Textfield3761 (202)",  # 225
        "perks_traits.8.effect": "Copy of Textfield3761 (203)",# 226
        "perks_traits.8.name": "Copy of Textfield3761 (204)",  # 227
        "perks_traits.8.rank": "Copy of Textfield3761 (205)",  # 228
        "perks_traits.9.effect": "Copy of Textfield3761 (206)",# 229
        "perks_traits.9.name": "Copy of Textfield3761 (207)",  # 230
        "perks_traits.9.rank": "Copy of Textfield3761 (208)",  # 231
        "perks_traits.10.effect": "Copy of Textfield3761 (209)",#232
        "perks_traits.10.name": "Copy of Textfield3761 (210)",  #233
        "perks_traits.10.rank": "Copy of Textfield3761 (211)",  #234
        "perks_traits.11.effect": "Copy of Textfield3761 (212)",#235
        "perks_traits.11.name": "Copy of Textfield3761 (213)",  #236
        "perks_traits.11.rank": "Copy of Textfield3761 (214)",  #237
        "perks_traits.12.effect": "Copy of Textfield3761 (215)",#238
        "perks_traits.12.name": "Copy of Textfield3761 (216)",  #239
        "perks_traits.12.rank": "Copy of Textfield3761 (217)"   #240
    }

    reader = PdfReader(str(args.input_pdf))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    # build the filled_fields dict, wrapping text in TextStringObject
    # and checkboxes in NameObject("/Yes") or NameObject("/Off")
    filled_fields = {}
    for key, field_name in field_map.items():
        raw = get_nested_value(data, key)
        if field_name.startswith("Copy of Checkbox"):
            checked = bool(raw)
            state = "Yes" if checked else "Off"
            pdf_val = NameObject(f"/{state}")
        else:
            pdf_val = TextStringObject(str(raw))
        filled_fields[field_name] = pdf_val

    # apply to every page
    for page in writer.pages:
        writer.update_page_form_field_values(page, filled_fields)
        

    # ensure viewers rebuild the look of each field
    writer._root_object["/AcroForm"].update({
        NameObject("/NeedAppearances"): BooleanObject(True)
    })

    # write out
    out_path = Path(args.output_pdf)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f:
        writer.write(f)

    print(f"✅ Flattened, filled PDF written to: {out_path}")

if __name__ == "__main__":
    main()
