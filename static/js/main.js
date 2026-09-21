/**
 * AI-Driven Early Anemia Risk Prediction - Main Client-Side JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // 2. Dynamic BMI Auto-Calculation in Assessment & Profile Forms
    const heightInput = document.getElementById('height');
    const weightInput = document.getElementById('weight');
    const bmiDisplay = document.getElementById('bmi_display');
    const bmiCategory = document.getElementById('bmi_category');

    function calculateBMI() {
        if (!heightInput || !weightInput || !bmiDisplay) return;

        const heightVal = parseFloat(heightInput.value);
        const weightVal = parseFloat(weightInput.value);

        if (heightVal > 0 && weightVal > 0) {
            // Convert height from cm to meters correctly: height_m = height_cm / 100
            const heightM = heightVal / 100.0;
            const bmi = weightVal / (heightM * heightM);
            const formattedBmi = bmi.toFixed(1);

            bmiDisplay.textContent = formattedBmi;

            if (bmiCategory) {
                if (bmi < 18.5) {
                    bmiCategory.textContent = "(Underweight)";
                    bmiCategory.className = "text-warning fw-semibold";
                } else if (bmi < 24.9) {
                    bmiCategory.textContent = "(Normal weight)";
                    bmiCategory.className = "text-success fw-semibold";
                } else if (bmi < 29.9) {
                    bmiCategory.textContent = "(Overweight)";
                    bmiCategory.className = "text-warning fw-semibold";
                } else {
                    bmiCategory.textContent = "(Obesity)";
                    bmiCategory.className = "text-danger fw-semibold";
                }
            }
        } else {
            bmiDisplay.textContent = "--";
            if (bmiCategory) bmiCategory.textContent = "";
        }
    }

    if (heightInput && weightInput) {
        heightInput.addEventListener('input', calculateBMI);
        weightInput.addEventListener('input', calculateBMI);
        // Initial run in case form pre-fills values
        calculateBMI();
    }
});
