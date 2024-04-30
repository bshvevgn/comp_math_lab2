<?php

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

header("Access-Control-Allow-Origin: http://localhost:3000");
header("Access-Control-Allow-Methods: POST");
header("Access-Control-Allow-Headers: Content-Type");

function processEquation($equation)
{
    $equation = preg_replace('/\s+/', '', $equation);

    $equation = preg_replace_callback('/(\d*)x\^(\d+)/', function ($matches) {
        return "pow(x, {$matches[2]})";
    }, $equation);

    $equation = preg_replace_callback('/sqrt\(([^)]+)\)/', function ($matches) {
        return "sqrt({$matches[1]})";
    }, $equation);

    $equation = preg_replace('/cos/', 'cos', $equation);
    $equation = preg_replace('/sin/', 'sin', $equation);
    $equation = preg_replace('/tg/', 'tan', $equation);
    $equation = preg_replace('/ctg/', 'cot', $equation);
    $equation = preg_replace('/(?<!\w)ln/', 'log', $equation);

    return $equation;
}

function f($x, $equation)
{
    $equation = processEquation($equation);
    $equation = str_replace('x', $x, $equation);
    return eval ("return {$equation};");
}

function isConvergent($equation, $intervalA, $intervalB)
{
    // Проверяем условие сходимости на интервале
    $x = $intervalA;
    while ($x <= $intervalB) {
        $derivative = df($x, $equation);
        if (abs($derivative) >= 1) {
            return false;
        }
        $x += 0.1; // Шаг для проверки
    }
    return true;
}

function simple_iteration_method($equation, $x0, $eps, $intervalA, $intervalB)
{
    // Проверяем условие сходимости
    if (!isConvergent($equation, $intervalA, $intervalB)) {
        return "Метод простой итерации не сходится на данном интервале";
    }

    $x = $x0;
    $iter_count = 0;
    while (true) {
        $iter_count++;
        $x_new = f($x, $equation);
        if (abs($x_new - $x) < $eps) {
            return [$x_new, $iter_count];
        }
        $x = $x_new;
    }
}

function chordMethod($equation, $a, $b, $eps = 1e-6, $maxIter = 3000)
{
    $rootCount = 0;
    $rootA = f($a, $equation);
    $rootB = f($b, $equation);

    if ($rootA * $rootB > 0) {
        // Если функция имеет одинаковые знаки на концах интервала,
        // то корень на этом интервале отсутствует
        return "На указанном интервале отсутствуют корни";
    } elseif ($rootA * $rootB == 0) {
        // Если функция равна нулю на одном из концов интервала,
        // то это и есть корень
        return ($rootA == 0) ? $a : $b;
    } else {
        // Если на концах интервала функция имеет разные знаки,
        // то на интервале может быть корень или несколько корней
        // Найдем их количество с помощью метода пол. деления
        $rootCount = 1; // Первый корень нашли уже на концах интервала
        $left = $a;
        $right = $b;
        $mid = ($left + $right) / 2;
        $maxIter = 100;
        $epsilon = 1e-6;

        for ($i = 0; $i < $maxIter; $i++) {
            $fMid = f($mid, $equation);
            if (abs($fMid) < $epsilon) {
                return [$mid, $i];
            }

            if ($fMid * $rootA > 0) {
                // Если знак функции на середине и левом конце одинаковый,
                // то корень находится между серединой и правым концом
                $left = $mid;
            } else {
                // Иначе корень находится между левым концом и серединой
                $right = $mid;
            }

            // Пересчитываем середину интервала
            $mid = ($left + $right) / 2;
            $rootCount++;
        }

        if ($i == $maxIter) {
            return "Превышено максимальное количество итераций";
        }
    }

    return "На указанном интервале найдено несколько корней";
}

function df($x, $equation)
{
    $h = 1e-6;
    return (f($x + $h, $equation) - f($x - $h, $equation)) / (2 * $h);
}

function newton_method($equation, $x0, $epsilon, $max_iter = 1000)
{
    $iter_count = 0;
    $x1 = 0;
    while ($iter_count < $max_iter) {
        $x1 = $x0 - f($x0, $equation) / df($x0, $equation);
        if (abs($x1 - $x0) < $epsilon) {
            return [$x1, $iter_count];
        }
        $x0 = $x1;
        $iter_count++;
    }
    return ["Метод Ньютона не сошелся к корню", $iter_count];

}

$methodChoice = isset($_GET['method']) ? intval($_GET['method']) : null;
$equation = isset($_GET['equation']) ? $_GET['equation'] : null;
$epsilon = isset($_GET['epsilon']) ? floatval($_GET['epsilon']) : null;
$intervalA = isset($_GET['intervalA']) ? floatval($_GET['intervalA']) : null;
$intervalB = isset($_GET['intervalB']) ? floatval($_GET['intervalB']) : null;
$approx = isset($_GET['approx']) ? floatval($_GET['approx']) : null;

$epsilon = $_GET['epsilon'];

if ($methodChoice === 1) {
    $root = chordMethod($equation, $intervalA, $intervalB, $epsilon);
    echo json_encode(['result' => $root]);
} elseif ($methodChoice === 2) {
    list($root, $iterations) = newton_method($equation, $approx, $epsilon);
    echo json_encode(['result' => $root, 'iterations' => $iterations]);
} elseif ($methodChoice === 3) {
    $root = simple_iteration_method($equation, $approx, $epsilon, $intervalA, $intervalB);
    echo json_encode(['result' => $root]);
} elseif ($methodChoice === 4) {
    $arg1 = '"' . $_GET['func1'] . '"';
    $arg2 = '"' . $_GET['func2'] . '"';
    $arg3 = $_GET['x_1_lower_bound'];
    $arg4 = $_GET['x_1_upper_bound'];
    $arg5 = $_GET['x_2_lower_bound'];
    $arg6 = $_GET['x_2_upper_bound'];
    $arg7 = $epsilon;

    $result = shell_exec("python3 simple-iteration.py $arg1 $arg2 $arg3 $arg4 $arg5 $arg6 $arg7")[0];
    echo json_encode(['result' => $result]);
} else {
    echo json_encode(['result' => "Метод не выбран"]);
}

// $result = shell_exec("python3 -m venv .venv");
// $result = shell_exec("source .venv/bin/activate");
// $result = shell_exec("pip3 install sympy");
?>