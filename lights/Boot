var pixelCount = 10; // Number of LEDs
var cycleDurations = [3000, 2000, 1500, 1000, 500]; // Durations for each cycle in milliseconds
var totalCycles = cycleDurations.length;
var cycleIndex = 0;
var cycleStartTime;

var boltMin = floor(pixelCount / 15);
var boltMax = ceil(pixelCount / 6);
var fade = 15;

var pixels = array(pixelCount);
var x = 0;
var timer = 0;

function initializeCycle() {
  cycleStartTime = time(.1); // Record the start time for the current cycle
  timer = cycleDurations[cycleIndex] / pixelCount; // Set the timer based on the current cycle duration
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

export function beforeRender(delta) {
  if (!cycleStartTime) {
    cycleStartTime = time(.1); // Record the start time for the sequence
    initializeCycle();
  }

  // Calculate the elapsed time in milliseconds for the current cycle
  var elapsedTime = (time(.1) - cycleStartTime) * 1000;

  if (elapsedTime > cycleDurations[cycleIndex]) {
    // Move to the next cycle
    cycleIndex++;
    if (cycleIndex >= totalCycles) {
      // Reset to the first cycle if all cycles are completed
      cycleIndex = 0;
    }
    initializeCycle();
  }

  // Fade effect
  for (var i = 0; i < pixelCount; i++) {
    pixels[i] -= (pixels[i] * fade * (delta / 1000)) + (1 >> 16);
  }

  timer -= delta;

  if (timer <= 0) {
    var boltSize = boltMin + random(boltMax - boltMin);
    while (boltSize-- > 0 && x < pixelCount) {
      pixels[x++] = 1;
    }

    timer = cycleDurations[cycleIndex] / pixelCount; // Set the timer for the next step

    if (x >= pixelCount) {
      x = 0;
      timer = cycleDurations[cycleIndex] / pixelCount; // Reset the timer for the new cycle
    }
  }
}

export function render(index) {
  var v = pixels[index];

  // Calculate the hue based on the index to create a rainbow effect
  var hue = index / pixelCount;

  hsv(hue, 1, v);
}
