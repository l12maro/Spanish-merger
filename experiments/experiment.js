// Experiment: Ceceo and seseo social perception in Spanish speakers
// Matched-guise experiment
// Regan (2022)

//const { fillerItems } = require("./stimuli");

const jsPsych = initJsPsych({
  on_finish: function () {
    jsPsych.data.displayData("csv");
  }
});

const subject_id = jsPsych.randomization.randomID(10);
const filename = `${subject_id}.csv`;



// --- Latin square assignment ---
// Randomly assign participant to one of 2 lists
const listNumber = Math.floor(Math.random() * 2);

// Assign conditions to items using Latin square
// const conditionNames = [
//   "ceceo",
//   "seseo",
//   "control"
// ];

// function getConditionForItem(itemIndex, list) {
//   return conditionNames[(itemIndex + list) % conditionNames.length];
// }

function getExperimentalCondition(itemIndex, list) {

  // Version 0:
  // even items = ceceo
  // odd items = seseo

  if (list === 0) {
    return itemIndex % 2 === 0
      ? "ceceo"
      : "seseo";
  }

  // Version 1:
  // reversed assignment

  return itemIndex % 2 === 0
    ? "seseo"
    : "ceceo";
}

// Build a trial: play audio for the assigned condition and then show
// all questions from `questionItems` (from stimuli.js). Returns an array
// of jsPsych trial objects.
 function buildTrial(item, conditionData, itemId, condition) {
   const audio = conditionData.audio || conditionData;

   let questionHTML = "";

  for (const q of questionItems) {

    // LIKERT SCALES
    if (q.scales) {

      questionHTML += `<div class="question-block">`;
      questionHTML += `<p><strong>${q.question || ""}</strong></p>`;

      q.scales.forEach((scale, i) => {

        questionHTML += `
          <p>${scale.prompt || `${scale.left} — ${scale.right}`}</p>
        `;

        for (let j = 1; j <= (scale.points || 5); j++) {

          questionHTML += `
            <label>
              <input
                type="radio"
                name="${q.id}_s${i + 1}"
                value="${j}"
                required
              >
              ${j}
            </label>
          `;
        }

        questionHTML += `<br><br>`;
      });

      questionHTML += `</div>`;
    }

    // MULTIPLE CHOICE
    else if (q.options && Array.isArray(q.options)) {

      questionHTML += `
        <div class="question-block">
          <p><strong>${q.question}</strong></p>
      `;

      q.options.forEach(option => {

        questionHTML += `
          <label>
            <input
              type="radio"
              name="${q.id}"
              value="${option}"
              required
            >
            ${option}
          </label><br>
        `;
      });

      questionHTML += `</div><br>`;
    }

    // TEXT QUESTIONS
    else if (q.type === 'text' || q.type === 'textarea') {

      questionHTML += `
        <div class="question-block">
          <p><strong>${q.question}</strong></p>
      `;

      if (q.type === "textarea") {

        questionHTML += `
          <textarea
            name="${q.id}"
            rows="4"
            cols="50"
            placeholder="${q.placeholder || ''}"
          ></textarea>
        `;

      } else {

        questionHTML += `
          <input
            type="text"
            name="${q.id}"
            placeholder="${q.placeholder || ''}"
          >
        `;
      }

      questionHTML += `</div><br>`;
    }
  }

  return [{
    type: jsPsychSurveyHtmlForm,

    html: `
      <p>Escucha el audio tantas veces como quieras y responde a las siguientes preguntas</p>

      <audio controls>
        <source src="${audio}" type="audio/ogg">
        Este elemento no es compatible con tu navegador.
      </audio>

      <hr>

      ${questionHTML}
    `,

    button_label: "Continuar",

    data: {
      task: 'audio_questions',
      item_id: itemId,
      condition: condition,
      audio: audio
    }
  }];
}


// --- Instructions ---
const welcomeScreen = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: `
    <div class="instructions">
      <h2>Bienvenido</h2>
      <p>Algunos estudios recientes de la psicología social han demostrado que se puede inferir mucho sobre una persona sólo por escuchar su manera de hablar.</p>
      <p>Vas a escuchar unas grabaciones y responder un cuestionario basado en tus intuiciones.</p>
      <p>Pulsa <strong>Espacio</strong> para continuar.</p>
    </div>
  `,
  choices: [" "]
};

const instructionsScreen = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: `
    <div class="instructions">
      <h2>Las instrucciones</h2>
      <p>Vas a escuchar a <u>10 personas</u>. Cada grabación dura entre <u>2-5 segundos</u>. Escucha las grabaciones tantas veces como quieras. Debes responder a las preguntas después de cada grabación.</p>
      <p>Debes estar en un lugar sin ruido y ponerte <strong><u>los auriculares</u></strong> para poder escuchar bien cada grabación. El estudio <strong><u>durará 15 minutos</u></strong>. No lo pienses demasiado, debes usar tus primeras intuiciones.</p>
      <p>Pulsa <strong>Espacio</strong> para comenzar.</p>
    </div>
  `,
  choices: [" "]
};

const restBreak = {
  type: jsPsychHtmlKeyboardResponse, 
  stimulus: `
    <div class="instructions">
      <h2>Rest Break</h2>
      <p>You are halfway through the experiment. Please take a short break.</p>
      <p>When you are ready to continue, press <strong>Space</strong>.</p>
    </div>
  `,
  choices: [" "]
};

// --- Build experimental block ---
// Assign conditions to critical items
// Copy fillers so we can remove used ones
let remainingFillers = [...fillerItems];

const experimentalTrials = [];

 for (let i = 0; i < criticalItems.length; i++) {
   const item = criticalItems[i];
   const filler = fillerItems[i % fillerItems.length]; // Cycle through fillers if fewer than critical items
  //  const condition = getConditionForItem(i, listNumber);
  //  const conditionData = item.conditions[condition];

    // Add ONE experimental guise
    const experimentalCondition =
      getExperimentalCondition(i, listNumber);

    experimentalTrials.push({
     itemId: item.id,
     condition: experimentalCondition,
     conditionData: item.conditions[experimentalCondition],
     audio: item.conditions[experimentalCondition].audio
   });

     // Add filler trial
     if (i > 3) {
// Pick a random valid filler
      const randomIndex =
      Math.floor(Math.random() * validFillers.length);

      const selectedFiller = validFillers[randomIndex];

      experimentalTrials.push({
      itemId: selectedFiller.id,
      condition: "filler",
      audio: selectedFiller.audio
    });

    // Remove used filler so it cannot repeat
    remainingFillers = remainingFillers.filter(
      filler => filler.id !== selectedFiller.id
    );
    };
  }

// Shuffle the experimental trials
function shuffle(array) {
  const arr = [...array];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

 const shuffledTrials = shuffle(experimentalTrials);

// Split into two halves for rest break
 const halfPoint = Math.ceil(shuffledTrials.length / 2);
 const firstHalf = shuffledTrials.slice(0, halfPoint);
 const secondHalf = shuffledTrials.slice(halfPoint);

 function buildTrialBlock(trialList) {
   const timeline = [];
   for (const trial of trialList) {
     const Trials = buildTrial(
       trial,
       trial.conditionData,
       trial.itemId,
       trial.condition,
     );
     timeline.push(...Trials);
   }
   return timeline;
 }

 const firstBlock = buildTrialBlock(firstHalf);
 const secondBlock = buildTrialBlock(secondHalf);




// --- Debrief ---
const debrief = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: `
      <div class="instructions">
        <h2>Experimento Completado</h2>
        <p>Gracias por tu participación!</p>
        <p>Presiona <strong>Espacio</strong> para ver tus datos.</p>
      </div>
    `
};

const save_data = {
  type: jsPsychPipe,
  action: "save",
  experiment_id: "T8BJlXfl1ZUY",
  filename: filename,
  data_string: ()=>jsPsych.data.get().csv()
};

// --- Run experiment ---
const timeline = [
  welcomeScreen,
  instructionsScreen,
  ...firstBlock,
//  restBreak,
  ...secondBlock,
  debrief,
  save_data
];

jsPsych.run(timeline);
