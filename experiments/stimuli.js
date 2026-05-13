// Experiment stimuli: Ceceo and seseo social perception in Spanish speakers
// Matched-guise experiment
// Regan (2022)
//
// 3 conditions:
//   - ceceo: /theta/ in all positions (ceceo pronunciation)
//   - seseo: /s/ in all positions (seseo pronunciation)
//   - control: sentences without coronal fricatives (control pronunciation)
//
// This file lists critical items (paired ceceo/seseo audio), filler items,
// and questionnaire items. Audio paths are relative to the `experiments/`
// directory (e.g. "../data/ceceo-I.ogg").

const criticalItems = [
  {
    id: 1,
    conditions: {
      ceceo: { audio: "../data/ceceo-I.ogg" },
      seseo: { audio: "../data/seseo-I.ogg" },
    },
    gender: "F"
  },
  {
    id: 2,
    conditions: {
      ceceo: { audio: "../data/ceceo-Isa.ogg" },
      seseo: { audio: "../data/seseo-Isa.ogg" },
    },
    gender: "F"
  },
  {
    id: 3,
    conditions: {
      ceceo: { audio: "../data/ceceo-L.ogg" },
      seseo: { audio: "../data/seseo-L.ogg" },
    },
    gender: "F"
  },
  {
    id: 4,
    conditions: {
      ceceo: { audio: "../data/ceceo-M.ogg" },
      seseo: { audio: "../data/seseo-M.ogg" },
    },
    gender: "M"
  },
  {
    id: 5,
    conditions: {
      ceceo: { audio: "../data/ceceo-R.ogg" },
      seseo: { audio: "../data/seseo-R.ogg" },
    },
    gender: "M"
  },
  {
    id: 6,
    conditions: {
      ceceo: { audio: "../data/ceceo-V.ogg" },
      seseo: { audio: "../data/seseo-V.ogg" },
    },
    gender: "V"
  }
];

// Insert control/filler items here (sentences without coronal fricatives)
const fillerItems = [
  { id: "1", audio: "../data/filler-D.ogg" },
  { id: "2", audio: "../data/filler-I.ogg" },
  { id: "3", audio: "../data/filler-L.ogg" },
  { id: "4", audio: "../data/filler-M.ogg" },
]

// Questionnaire items presented after each trial.
const questionItems = [
  {
    id: "q1",
    question: "Esta persona suena...",
    // Six 6-point Likert scales. Each scale is an object with `left` and `right`
    // labels and an optional `points` field (default 5).
    scales: [
      { left: "de nivel socioeconomico bajo", right: "de nivel socioeconomico alto", points: 6 },
      { left: "con menos estudios", right: "con más estudios", points: 6 },
      { left: "menos masculina", right: "más masculina", points: 6 },
      { left: "menos simpática", right: "más simpática", points: 6 },
      { left: "más rural", right: "más urbana", points: 6 },
      { left: "informal", right: "formal", points: 6 }
    ]
  },
  {
    id: "q2",
    question: "¿A qué crees que se dedica esta persona?",
    type: "select",
    options: [
      "trabaja en un bar/restaurante",
      "trabaja en la construcción",
      "trabaja en una tienda",
      "trabaja en el campo",
      "es administrador/a",
      "es maestro/a",
      "es médico/a o abogado/a"
    ]
  },
  {
    id: "q3",
    question: "¿Qué edad crees que tiene?",
    type: "select",
    options: [
      "< 30",
      "30-39",
      "40-49",
      "50-59",
      "> 60"
    ]
  },
  {
    id: "q4",
    question: "¿De dónde crees que es esta persona?",
    type: "select",
    options: ["Huelva", "Sevilla", "Otro lugar"],
  },
  {
    id: "q5",
    question: "¿Algo más que se te ocurre de esta persona?",
    type: "text"  
  },
]

// Export for module environments if needed
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { criticalItems, fillerItems, questionItems };
}
