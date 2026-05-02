// Experiment: Ceceo and seseo social perception in Spanish speakers
// Matched-guise experiment
// Regan (2022)

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
const conditionNames = [
  "ceceo",
  "seseo",
  "control"
];

function getConditionForItem(itemIndex, list) {
  return conditionNames[(itemIndex + list) % conditionNames.length];
}

// Build a trial: play audio for the assigned condition and then show
// all questions from `questionItems` (from stimuli.js). Returns an array
// of jsPsych trial objects.
 function buildTrial(item, conditionData, itemId, condition) {
   const trials = [];
   const audio = conditionData.audio || conditionData;


  // Audio playback trial
   if (audio) {
     trials.push({
      type: jsPsychSurveyHtmlForm,
      stimulus: audio,
      html: `
        <p>Listen to the audio below as many times as you like:</p>
        <audio controls>
          <source src="${trial.audio}" type="audio/mpeg">
          Your browser does not support the audio element.
        </audio> `,
      // choices: "NO_KEYS",
      // trial_ends_after_audio: false,
      // prompt: '<p>Escucha la grabación.</p>',
      data: {
         task: 'listening',
         item_id: itemId,
         condition: condition,
         audio: audio,
       }
     });
   }
   return trials;
 }

  // --- Build comprehension question trial ---
  //---function buildQuestionTrial() {
    // for (const q of questionItems) {
      // if (q.scales) {
        // const likertQs = q.scales.map((scale, i) => ({
          // prompt: scale.prompt || `${scale.left} — ${scale.right}`,
          // name: `${q.id}_s${i + 1}`,
          // labels: Array((scale.points || 5)).fill().map((_, idx) => String(idx + 1))
        // }));

        // trials.push({
          // type: jsPsychSurveyLikert,
          // questions: likertQs,
          // data: { task: 'likert', item_id: criticalItem.id, question_id: q.id, condition: assignedCondition, audio: audioPath }
        // });

      // } else if (q.options && Array.isArray(q.options)) {
        // trials.push({
          // type: jsPsychSurveyMultiChoice,
          // questions: [{ prompt: q.question, name: q.id, options: q.options, required: true }],
          // data: { task: 'choice', item_id: criticalItem.id, question_id: q.id, condition: assignedCondition, audio: audioPath }
        // });

      // } else if (q.type === 'text' || q.type === 'textarea') {
        // trials.push({
          // type: jsPsychSurveyText,
          // questions: [{ prompt: q.question, name: q.id, placeholder: q.placeholder || '' }],
          // data: { task: 'text', item_id: criticalItem.id, question_id: q.id, condition: assignedCondition, audio: audioPath }
        // });

      // } 
    // }
  // }


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
      <p>Vas a escuchar a <u>24 personas</u>. Cada grabación dura entre <u>2-5 segundos</u>. Escucha las grabaciones tantas veces como quieras. Debes responder a las preguntas después de cada grabación.</p>
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
const experimentalTrials = [];

// for (let i = 0; i < criticalItems.length; i++) {
//   const item = criticalItems[i];
//   const condition = getConditionForItem(i, listNumber);
//   const conditionData = item.conditions[condition];

//    experimentalTrials.push({
    // itemId: item.id,
    // condition: condition,
    // conditionData: conditionData,
    // audio: conditionData.audio
  // });
// }

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
//    timeline.push(...buildQuestionTrial());
   }
   return timeline;
 }

 const firstBlock = buildTrialBlock(firstHalf);
 const secondBlock = buildTrialBlock(secondHalf);

const testAudio = {
    type: jsPsychAudioKeyboardResponse,
    stimulus: 'ceceo-I.ogg',
    choices: ' ',
    prompt: "Press space to continue after listening to the audio.",
    response_ends_trial: true
};


// Step 1: Audio + questionnaire
    const audioQuestionTrial = {
      type: jsPsychSurveyHtmlForm,
      html: `
        <p>Listen to the audio below as many times as you like:</p>
        <audio controls>
          <source src="ceceo-I.ogg" type="audio/mpeg">
          Your browser does not support the audio element.
        </audio> `
    };

    // Step 2: Continue button
    const continueButton = {
      type: jsPsychHtmlButtonResponse,
      stimulus: "<p>Press continue to go to the next audio.</p>",
      choices: ["Continue"]
    };

  //  trialTimeline.push(audioQuestionTrial);
  //  trialTimeline.push(continueButton);
  //});


// --- Debrief ---
const debrief = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: `
      <div class="instructions">
        <h2>Experiment Complete</h2>
        <p>Thank you for your participation!</p>
        <p>Press <strong>Space</strong> to see your data.</p>
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
//  audioQuestionTrial,
//  continueButton,
  ...firstBlock,
  restBreak,
//  ...secondBlock,
  debrief,
//  save_data
];

jsPsych.run(timeline);
