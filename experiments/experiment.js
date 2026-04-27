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
//  instructionsScreen,
//  ...firstBlock,
//  restBreak,
//  ...secondBlock,
//  debrief,
//  save_data
];

jsPsych.run(timeline);
