/* face-texture-map.js — preset number -> No Mercy face texture file.
   Pure (DOM-free) data + lookup for the Creation Suite FACE panel.
   Source of truth (verified 2026-10-24 against the live repo listing):
   `customization/parts/no-mercy/faces/` holds 146 PNGs — 98 male
   (Face_Male_01 .. Face_Male_98, no gaps), 20 female (Face_Female_01 ..
   Face_Female_20, no gaps), and 28 extras with no preset number
   (unnumbered Face_1Exx files + named duplicates). A wwe-layer preset
   in `customization/templates/face-presets.json` carries
   { gender, no_mercy_face } and resolves by number into the male/female
   table below; gnm-layer presets carry no texture and resolve to null
   (expression bake only). UI rule: the suite shows the preset's neutral
   name (Classic Hero, Rugged, ...) — filenames below are repo asset
   paths used to load the texture, never displayed as character names.
   The suite composes the load URL as
   '../parts/no-mercy/faces/' + file (page: customization/creation-suite-ui/). */

export const FACE_TEXTURES_MALE = [
  'Face_Male_01_The_Rock_1D72.png',
  'Face_Male_02_Stone_Cold_1D74.png',
  'Face_Male_03_Undertaker_1D76.png',
  'Face_Male_04_Mankind_1D7A.png',
  'Face_Male_05_CactusFoley_1D7C.png',
  'Face_Male_06_HBK_1D7E.png',
  'Face_Male_07_HHH_1D80.png',
  'Face_Male_08_X-Pac_1D82.png',
  'Face_Male_09_Billy_Gunn_1D84.png',
  'Face_Male_10_Road_Dogg_1D86.png',
  'Face_Male_11_Benoit_1D88.png',
  'Face_Male_12_Malenko_1D8A.png',
  'Face_Male_13_Saturn_1D8C.png',
  'Face_Male_14_Eddy_1D8E.png',
  'Face_Male_15_Jericho_1D90.png',
  'Face_Male_16_Angle_1D92.png',
  'Face_Male_17_Tazz_1D94.png',
  'Face_Male_18_Test_1D96.png',
  'Face_Male_19_Godfather_1D98.png',
  'Face_Male_20_DLo_1D9A.png',
  'Face_Male_21_Venis_1D9C.png',
  'Face_Male_22_Shamrock_1D9E.png',
  'Face_Male_23_Rikishi_1DA0.png',
  'Face_Male_24_Grand_Master_1DA2.png',
  'Face_Male_25_Scotty_1DA4.png',
  'Face_Male_26_Edge_1DA6.png',
  'Face_Male_27_Christian_1DA8.png',
  'Face_Male_28_Matt_1DAA.png',
  'Face_Male_29_Jeff_1DAC.png',
  'Face_Male_30_Faarooq_1DAE.png',
  'Face_Male_31_Bradshaw_1DB0.png',
  'Face_Male_32_D-Von_1DB2.png',
  'Face_Male_33_Buh_Buh_1DB4.png',
  'Face_Male_34_Hardcore_1DB6.png',
  'Face_Male_35_Crash_1DB8.png',
  'Face_Male_36_Boss_Man_1DBA.png',
  'Face_Male_37_Albert_1DBC.png',
  'Face_Male_38_Al_Snow_1DBE.png',
  'Face_Male_39_Blackman_1DC0.png',
  'Face_Male_40_Bulldog_1DC2.png',
  'Face_Male_41_Henry_1DC4.png',
  'Face_Male_42_Viscera_1DC6.png',
  'Face_Male_43_Gangrel_1DC8.png',
  'Face_Male_44_Buchannon_1DCA.png',
  'Face_Male_45_Rios_1DCC.png',
  'Face_Male_46_TAKA_1DCE.png',
  'Face_Male_47_Funaki_1DD0.png',
  'Face_Male_48_Vince_1DD2.png',
  'Face_Male_49_Shane_1DD4.png',
  'Face_Male_50_King_1DD6.png',
  'Face_Male_51_JR_1DD8.png',
  'Face_Male_52_Bearer_1DDA.png',
  'Face_Male_53_Brisco_1DDC.png',
  'Face_Male_54_Patterson_1DDE.png',
  'Face_Male_55_Finkel_1DE0.png',
  'Face_Male_56_Hebner_1DE4.png',
  'Face_Male_57_Michael_Cole_1DE6.png',
  'Face_Male_58_Andre_1DE8.png',
  'Face_Male_59_Rodney_1E10.png',
  'Face_Male_60_Joey_Abs_1E12.png',
  'Face_Male_61_Pete_Gas_1E0E.png',
  'Face_Male_62_Richards_1E14.png',
  'Face_Male_63_Mosh_1E16.png',
  'Face_Male_64_Thrasher_1E18.png',
  'Face_Male_65_Mideon_1E1A.png',
  'Face_Male_66_Droz_1E1C.png',
  'Face_Male_67_Kane_1DE2.png',
  'Face_Male_68_Default_CAW_Face_1E1E.png',
  'Face_Male_69_Akira_Taue_1E20.png',
  'Face_Male_70_1E22.png',
  'Face_Male_71_Stan_Hansen_1E24.png',
  'Face_Male_72_1E26.png',
  'Face_Male_73_1E28.png',
  'Face_Male_74_1E2A.png',
  'Face_Male_75_1E2C.png',
  'Face_Male_76_1E2E.png',
  'Face_Male_77_1E30.png',
  'Face_Male_78_1E32.png',
  'Face_Male_79_1E34.png',
  'Face_Male_80_1E36.png',
  'Face_Male_81_1E38.png',
  'Face_Male_82_1E3A.png',
  'Face_Male_83_1E3C.png',
  'Face_Male_84_1E3E.png',
  'Face_Male_85_1E40.png',
  'Face_Male_86_1E42.png',
  'Face_Male_87_1E44.png',
  'Face_Male_88_1E46.png',
  'Face_Male_89_1E48.png',
  'Face_Male_90_1E4A.png',
  'Face_Male_91_1E4C.png',
  'Face_Male_92_1E4E.png',
  'Face_Male_93_1E50.png',
  'Face_Male_94_1E52.png',
  'Face_Male_95_1E54.png',
  'Face_Male_96_1E56.png',
  'Face_Male_97_1E58.png',
  'Face_Male_98_Edge_WM2K_1E5E.png',
];

export const FACE_TEXTURES_FEMALE = [
  'Face_Female_01_Chyna_1DEA.png',
  'Face_Female_02_Stephanie_1DEC.png',
  'Face_Female_03_Tori_1DEE.png',
  'Face_Female_04_Terri_1DF0.png',
  'Face_Female_05_Kat_1DF2.png',
  'Face_Female_06_Lita_1DF4.png',
  'Face_Female_07_Ivory_1DF6.png',
  'Face_Female_08_Jacqueline_1DF8.png',
  'Face_Female_09_Linda_1DFA.png',
  'Face_Female_10_Debra_1DFC.png',
  'Face_Female_11_Trish_1DFE.png',
  'Face_Female_12_Mae_Young_1E00.png',
  'Face_Female_13_Moolah_1E02.png',
  'Face_Female_14_1E04.png',
  'Face_Female_15_Ho_2_1E06.png',
  'Face_Female_16_1E08.png',
  'Face_Female_17_Ho_1_1E0A.png',
  'Face_Female_18_Ho_3_1E0C.png',
  'Face_Female_19_1E5A.png',
  'Face_Female_20_1E5C.png',
];

export const FACE_TEXTURES_EXTRA = [
  'Face_1E6F.png',
  'Face_1E70.png',
  'Face_1E71.png',
  'Face_1E72.png',
  'Face_1E73.png',
  'Face_1E74.png',
  'Face_1E75.png',
  'Face_1E76.png',
  'Face_1E77.png',
  'Face_1E78.png',
  'Face_1E79.png',
  'Face_1E7A.png',
  'Face_1E7B.png',
  'Face_1E7C.png',
  'Face_1E7D.png',
  'Face_Austin_1E7F.png',
  'Face_Big_Show_1E81.png',
  'Face_DLo_1E8D.png',
  'Face_Foley_1E83.png',
  'Face_HBK_1E85.png',
  'Face_HHH_1E87.png',
  'Face_Jeff_Hardy_1E95.png',
  'Face_Ken_Shamrock_1E91.png',
  'Face_Matt_Hardy_1E93.png',
  'Face_RROR_Big_Show_1D78.png',
  'Face_Road_Dogg_1E8B.png',
  'Face_Val_Venis_1E8F.png',
  'Face_X-Pac_1E89.png',
];

/* Resolve a face preset object (from face-presets.json) to its texture
   filename, or null when the preset has no live texture (gnm layer,
   unknown gender/number). Numbers are 1-based into the tables above. */
export function faceTextureForPreset(preset) {
  if (!preset || preset.layer !== 'wwe') return null;
  const n = Number(preset.no_mercy_face);
  if (!Number.isInteger(n) || n < 1) return null;
  if (preset.gender === 'male') return FACE_TEXTURES_MALE[n - 1] || null;
  if (preset.gender === 'female') return FACE_TEXTURES_FEMALE[n - 1] || null;
  return null;
}

export function faceTextureCount() {
  return FACE_TEXTURES_MALE.length + FACE_TEXTURES_FEMALE.length + FACE_TEXTURES_EXTRA.length;
}
