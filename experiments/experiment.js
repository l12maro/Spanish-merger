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
  return conditionNames[(itemIndex + list) % 3];
}

// --- Build evaluation question trial ---
function buildQuestionTrial(question, itemId) {
  if (!question) return [];
  return [
    {
      type: jsPsychHtmlKeyboardResponse,
      stimulus: `
        <div class="comprehension-question">
          <p>${question.text}</p>
          <p style="font-size: 16px; color: #666;"><strong>F</strong> = Yes &nbsp;&nbsp;&nbsp; <strong>J</strong> = No</p>
        </div>
      `,
      choices: ["f", "j"],
      data: {
        task: "comprehension",
        item_id: itemId,
        correct_answer: question.correct,
        question_text: question.text
      },
      on_finish: function (data) {
        const response = data.response;
        const isYes = response === "f";
        data.participant_answer = isYes ? "yes" : "no";
        data.correct = data.participant_answer === data.correct_answer;
      }
    }
  ];
}

// --- Build audio trial (if an audio file is provided in stimuli) ---
function buildAudioTrial(trial) {
  const conditionData = trial.conditionData || {};
  let audioPath = null;
  if (conditionData && conditionData.audio) {
    audioPath = conditionData.audio;
  } else if (typeof audioMap !== 'undefined' && audioMap[trial.itemId] && audioMap[trial.itemId][trial.condition]) {
    audioPath = audioMap[trial.itemId][trial.condition];
  }
  if (!audioPath) return [];

  return [
    {
      type: jsPsychAudioKeyboardResponse,
      stimulus: audioPath,
      choices: [" "],
      prompt: '<p>Press <strong>Space</strong> to continue.</p>',
      data: {
        task: "listening",
        item_id: trial.itemId,
        condition: trial.condition || "filler",
        audio: audioPath,
        is_critical: trial.isCritical,
        list: listNumber
      }
    }
  ];
}

// --- Instructions ---
const welcomeScreen = {
  type: jsPsychHtmlKeyboardResponse,
  stimulus: `
    <div class="instructions">
      <h2>Bienvenido</h2>
      <p>Algunos estudios recientes de la psicología social han demostrado que se puede inferir mucho sobre una persona sólo por escuchar su manera de hablar.</p>
      <p>Vas a escuchar unas grabaciones y responder un cuestionario basado en tus intuiciones.</p>
      <p>Pulsa<strong>Espacio</strong> para continuar.</p>
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
      <p>Pulsa<strong>Espacio</strong> para comenzar.</p>
    </div>
  `,
  choices: [" "]
};

// --- Build experimental block ---
// Assign conditions to critical items
const experimentalTrials = [];

for (let i = 0; i < criticalItems.length; i++) {
  const item = criticalItems[i];
  const condition = getConditionForItem(i, listNumber);
  const conditionData = item.conditions[condition];

  experimentalTrials.push({
    itemId: item.id,
    condition: condition,
    isCritical: true,
    conditionData: conditionData,
    question: item.question,
    segments: conditionData.segments
  });
}

// Add filler items
for (const item of fillerItems) {
  experimentalTrials.push({
    itemId: item.id,
    condition: "filler",
    isCritical: false,
    conditionData: { segments: item.segments },
    question: item.question,
    segments: item.segments
  });
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
    // Prefer audio if available, otherwise fall back to segmented text
    const audioTrials = buildAudioTrial(trial);
    if (audioTrials.length > 0) {
      timeline.push(...audioTrials);
    } else {
      const readingTrials = buildReadingTrials(
        trial,
        trial.conditionData,
        trial.itemId,
        trial.condition,
        trial.isCritical
      );
      timeline.push(...readingTrials);
    }
    if (trial.question) {
      timeline.push(...buildQuestionTrial(trial.question, trial.itemId));
    }
  }
  return timeline;
}

const firstBlock = buildTrialBlock(firstHalf);

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

const secondBlock = buildTrialBlock(secondHalf);

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
  ...firstBlock,
  restBreak,
  ...secondBlock,
  debrief,
  save_data
];

jsPsych.run(timeline);
