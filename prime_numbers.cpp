#include <iostream>
#include <vector>
#include <thread>
#include <atomic>
#include <chrono>
#include <cmath>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <algorithm>
#include <mutex>
#include <string>
#include <cstring>

class PrimeBenchmark {
private:
    std::atomic<long long> total_primes{0};
    std::atomic<long long> numbers_checked{0};
    std::atomic<long long> largest_prime{2};
    std::atomic<bool> stop_benchmark{false};
    std::vector<std::thread> threads;
    std::mutex results_mutex;
    int num_threads;
    int benchmark_duration;
    
public:
    PrimeBenchmark(int duration = 60) : benchmark_duration(duration) {
        num_threads = std::thread::hardware_concurrency();
        if (num_threads == 0) num_threads = 4;
    }
    
    bool is_prime(long long n) {
        if (n < 2) return false;
        if (n == 2 || n == 3) return true;
        if (n % 2 == 0 || n % 3 == 0) return false;
        
        long long i = 5;
        long long w = 2;
        while (i * i <= n) {
            if (n % i == 0) return false;
            i += w;
            w = 6 - w;
        }
        return true;
    }
    
    void prime_worker(int thread_id, long long start_num) {
        long long local_primes = 0;
        long long local_checked = 0;
        long long current = start_num;
        long long local_largest_prime = 2;
        
        while (!stop_benchmark) {
            if (is_prime(current)) {
                local_primes++;
                local_largest_prime = std::max(local_largest_prime, current);
                
                // Update global largest prime number
                long long current_largest = largest_prime.load();
                while (current > current_largest) {
                    if (largest_prime.compare_exchange_weak(current_largest, current)) {
                        break;
                    }
                }
            }
            local_checked++;
            current++;
            
            // Reset periodically to avoid overflow
            if (current > start_num + 1000000000) {
                current = start_num;
            }
        }
        
        total_primes += local_primes;
        numbers_checked += local_checked;
        
        // Final update of largest prime from this thread
        long long current_largest = largest_prime.load();
        while (local_largest_prime > current_largest) {
            if (largest_prime.compare_exchange_weak(current_largest, local_largest_prime)) {
                break;
            }
        }
    }
    
    void run_benchmark() {
        std::cout << "🚀 Starting CPU benchmark..." << std::endl;
        std::cout << "⏱️  Duration: " << benchmark_duration << " seconds" << std::endl;
        std::cout << "🧵 Number of threads: " << num_threads << std::endl;
        std::cout << "⚡ CPU load: 100%" << std::endl;
        std::cout << "🔍 Searching for prime numbers..." << std::endl;
        
        auto start_time = std::chrono::steady_clock::now();
        
        // Start threads
        for (int i = 0; i < num_threads; ++i) {
            threads.emplace_back(&PrimeBenchmark::prime_worker, this, i, i * 1000000LL + 2);
        }
        
        // Display progress every 5 seconds
        int elapsed_seconds = 0;
        while (elapsed_seconds < benchmark_duration && !stop_benchmark) {
            std::this_thread::sleep_for(std::chrono::seconds(5));
            elapsed_seconds += 5;
            
            auto current_time = std::chrono::steady_clock::now();
            auto current_duration = std::chrono::duration_cast<std::chrono::seconds>(current_time - start_time);
            
            std::cout << "⏳ Progress: " << current_duration.count() << "s | " 
                      << "Largest: " << largest_prime << std::endl;
        }
        
        // Wait until the end if needed
        if (elapsed_seconds < benchmark_duration) {
            int remaining = benchmark_duration - elapsed_seconds;
            std::this_thread::sleep_for(std::chrono::seconds(remaining));
        }
        
        // Stop threads
        stop_benchmark = true;
        
        for (auto& thread : threads) {
            thread.join();
        }
        
        auto end_time = std::chrono::steady_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
        
        std::cout << "✅ Benchmark completed!" << std::endl;
        std::cout << "📊 Results:" << std::endl;
        std::cout << "   Prime numbers found: " << total_primes << std::endl;
        std::cout << "   Numbers checked: " << numbers_checked << std::endl;
        std::cout << "   Largest prime number: " << largest_prime << std::endl;
        std::cout << "   Execution time: " << duration.count() / 1000.0 << "s" << std::endl;
    }
    
    void generate_html_report() {
        auto now = std::chrono::system_clock::now();
        auto now_time_t = std::chrono::system_clock::to_time_t(now);
        
        std::ostringstream html;
        html << R"(
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Monitor - C++ Prime Benchmark</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card h2 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.4em;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #3498db;
        }
        
        .metric.primes { border-left-color: #e74c3c; }
        .metric.checked { border-left-color: #2ecc71; }
        .metric.largest { border-left-color: #f39c12; }
        .metric.threads { border-left-color: #9b59b6; }
        .metric.performance { border-left-color: #1abc9c; }
        
        .metric .label {
            font-weight: 600;
            color: #2c3e50;
        }
        
        .metric .value {
            font-weight: bold;
            font-size: 1.1em;
            color: #2c3e50;
        }
        
        .largest-prime-display {
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-top: 15px;
            font-size: 1.2em;
            font-weight: bold;
        }
        
        .performance-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
            margin-top: 10px;
        }
        
        .elite { background: linear-gradient(135deg, #ffd700, #ffed4e); color: #000; }
        .excellent { background: linear-gradient(135deg, #c0c0c0, #e8e8e8); color: #000; }
        .very-good { background: linear-gradient(135deg, #cd7f32, #e89d4c); color: #000; }
        .good { background: linear-gradient(135deg, #27ae60, #2ecc71); color: white; }
        .average { background: linear-gradient(135deg, #3498db, #2980b9); color: white; }
        .basic { background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; }
        
        .charts {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .chart-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .chart {
            width: 100%;
            height: 200px;
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border-radius: 10px;
            display: flex;
            align-items: end;
            padding: 20px;
            gap: 10px;
        }
        
        .bar {
            flex: 1;
            background: linear-gradient(to top, #3498db, #2980b9);
            border-radius: 5px 5px 0 0;
            position: relative;
            transition: height 0.3s ease;
        }
        
        .bar.primes { background: linear-gradient(to top, #e74c3c, #c0392b); }
        .bar.performance { background: linear-gradient(to top, #2ecc71, #27ae60); }
        .bar.largest { background: linear-gradient(to top, #f39c12, #e67e22); }
        
        .bar-label {
            position: absolute;
            bottom: -25px;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 0.8em;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .system-info {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            color: white;
            opacity: 0.8;
        }
        
        @media (max-width: 768px) {
            .charts {
                grid-template-columns: 1fr;
            }
            
            .dashboard {
                grid-template-columns: 1fr;
            }
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .stat-item {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .prime-info {
            background: linear-gradient(135deg, #ff9a9e, #fad0c4);
            padding: 25px;
            border-radius: 15px;
            margin-top: 20px;
            text-align: center;
        }
        
        .prime-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
            margin: 15px 0;
            word-break: break-all;
        }
        
        .prime-label {
            font-size: 1.2em;
            color: #7f8c8d;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔢 C++ Prime Benchmark</h1>
            <div class="subtitle">CPU performance test - )" << benchmark_duration << R"( seconds full load</div>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h2>📊 Main Results</h2>
                <div class="metric primes">
                    <span class="label">Prime numbers found:</span>
                    <span class="value">)" << total_primes << R"(</span>
                </div>
                <div class="metric checked">
                    <span class="label">Numbers checked:</span>
                    <span class="value">)" << numbers_checked << R"(</span>
                </div>
                <div class="metric largest">
                    <span class="label">Largest prime number:</span>
                    <span class="value">)" << largest_prime << R"(</span>
                </div>
                <div class="metric threads">
                    <span class="label">Number of threads:</span>
                    <span class="value">)" << num_threads << R"(</span>
                </div>
                <div class="metric performance">
                    <span class="label">Performance (numbers/second):</span>
                    <span class="value">)" << (numbers_checked / benchmark_duration) << R"(</span>
                </div>
            </div>
            
            <div class="card">
                <h2>🏆 Performance Ranking</h2>
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>🏆 Elite:</span>
                        <span>> 10M numbers/second</span>
                    </div>
                    <div style="background: #f8f9fa; height: 8px; border-radius: 4px; overflow: hidden;">
                        <div style="background: linear-gradient(135deg, #ffd700, #ffed4e); height: 100%; width: 100%;"></div>
                    </div>
                </div>
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>🔥 Excellent:</span>
                        <span>5M - 10M</span>
                    </div>
                    <div style="background: #f8f9fa; height: 8px; border-radius: 4px; overflow: hidden;">
                        <div style="background: linear-gradient(135deg, #c0c0c0, #e8e8e8); height: 100%; width: 75%;"></div>
                    </div>
                </div>
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>💪 Very Good:</span>
                        <span>2M - 5M</span>
                    </div>
                    <div style="background: #f8f9fa; height: 8px; border-radius: 4px; overflow: hidden;">
                        <div style="background: linear-gradient(135deg, #cd7f32, #e89d4c); height: 100%; width: 50%;"></div>
                    </div>
                </div>
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>👍 Good:</span>
                        <span>1M - 2M</span>
                    </div>
                    <div style="background: #f8f9fa; height: 8px; border-radius: 4px; overflow: hidden;">
                        <div style="background: linear-gradient(135deg, #27ae60, #2ecc71); height: 100%; width: 25%;"></div>
                    </div>
                </div>
                <div class="performance-badge )" << get_performance_class() << R"(">
                    )" << get_performance_rank() << R"(
                </div>
            </div>
            
            <div class="card">
                <h2>📈 Statistics</h2>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-value">)" << std::fixed << std::setprecision(1) << (total_primes / (double)benchmark_duration) << R"(</div>
                        <div class="stat-label">Primes/second</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">)" << (numbers_checked / benchmark_duration) << R"(</div>
                        <div class="stat-label">Checks/second</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">)" << std::fixed << std::setprecision(2) << ((double)total_primes / numbers_checked * 100) << R"(%</div>
                        <div class="stat-label">Prime density</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">)" << num_threads << R"(</div>
                        <div class="stat-label">Active threads</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="prime-info">
            <div class="prime-label">🎯 Largest prime number found</div>
            <div class="prime-number">)" << largest_prime << R"(</div>
            <div style="color: #7f8c8d; font-size: 1.1em;">
                Number of digits: )" << std::to_string(largest_prime).length() << R"(
            </div>
        </div>
        
        <div class="charts">
            <div class="chart-container">
                <h2>📊 Processing Performance</h2>
                <div class="chart">
                    <div class="bar primes" style="height: )" << get_percentage_height(total_primes, 1000000) << R"(%;">
                        <div class="bar-label">Prime numbers</div>
                    </div>
                    <div class="bar performance" style="height: )" << get_percentage_height(numbers_checked, 100000000) << R"(%;">
                        <div class="bar-label">Checks</div>
                    </div>
                    <div class="bar largest" style="height: )" << get_percentage_height(std::to_string(largest_prime).length(), 20) << R"(%;">
                        <div class="bar-label">Largest digits</div>
                    </div>
                </div>
            </div>
            
            <div class="chart-container">
                <h2>🎯 Performance Rating</h2>
                <div style="text-align: center; padding: 40px 0;">
                    <div style="font-size: 3em; font-weight: bold; color: #2c3e50;">
                        )" << (numbers_checked / benchmark_duration) << R"(
                    </div>
                    <div style="font-size: 1.2em; color: #7f8c8d; margin-bottom: 15px;">
                        operations/second
                    </div>
                    <div class="performance-badge )" << get_performance_class() << R"(" style="margin-top: 15px;">
                        )" << get_performance_rank() << R"(
                    </div>
                </div>
            </div>
        </div>
        
        <div class="system-info">
            <h2>🖥️ System Information</h2>
            <div class="info-grid">
                <div class="info-item">
                    <span>Execution date:</span>
                    <span>)" << std::ctime(&now_time_t) << R"(</span>
                </div>
                <div class="info-item">
                    <span>Number of threads:</span>
                    <span>)" << num_threads << R"(</span>
                </div>
                <div class="info-item">
                    <span>Benchmark time:</span>
                    <span>)" << benchmark_duration << R"( seconds</span>
                </div>
                <div class="info-item">
                    <span>Benchmark type:</span>
                    <span>Prime numbers</span>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by C++ Prime Benchmark | )" << std::ctime(&now_time_t) << R"(</p>
        </div>
    </div>
</body>
</html>
)";

        std::ofstream file("benchmark_results.html");
        file << html.str();
        file.close();
        
        std::cout << "📄 HTML page generated: benchmark_results.html" << std::endl;
    }
    
private:
    std::string get_performance_rank() {
        long long ops_per_second = numbers_checked / benchmark_duration;
        if (ops_per_second > 10000000) return "🏆 Elite";
        if (ops_per_second > 5000000) return "🔥 Excellent";
        if (ops_per_second > 2000000) return "💪 Very Good";
        if (ops_per_second > 1000000) return "👍 Good";
        return "🔰 Average";
    }
    
    std::string get_performance_class() {
        long long ops_per_second = numbers_checked / benchmark_duration;
        if (ops_per_second > 10000000) return "elite";
        if (ops_per_second > 5000000) return "excellent";
        if (ops_per_second > 2000000) return "very-good";
        if (ops_per_second > 1000000) return "good";
        return "average";
    }
    
    int get_percentage_height(long long value, long long max_value) {
        double percentage = (double)value / max_value * 100;
        return std::min(100, (int)percentage);
    }
};

void print_usage(const char* program_name) {
    std::cout << "Usage: " << program_name << " [OPTIONS]" << std::endl;
    std::cout << "Options:" << std::endl;
    std::cout << "  -t SECONDS, --time SECONDS  Benchmark duration in seconds (default: 60)" << std::endl;
    std::cout << "  -h, --help                 Display this help message" << std::endl;
    std::cout << std::endl;
    std::cout << "Examples:" << std::endl;
    std::cout << "  " << program_name << "                    # 60 seconds (default)" << std::endl;
    std::cout << "  " << program_name << " -t 30             # 30 seconds" << std::endl;
    std::cout << "  " << program_name << " --time 120        # 2 minutes" << std::endl;
}

int main(int argc, char* argv[]) {
    int duration = 60; // Default time: 60 seconds
    
    // Parse command line arguments
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "-h" || arg == "--help") {
            print_usage(argv[0]);
            return 0;
        }
        else if (arg == "-t" || arg == "--time") {
            if (i + 1 < argc) {
                try {
                    duration = std::stoi(argv[++i]);
                    if (duration <= 0) {
                        std::cerr << "❌ Error: Time must be a positive number" << std::endl;
                        return 1;
                    }
                }
                catch (const std::exception& e) {
                    std::cerr << "❌ Error: Invalid time format" << std::endl;
                    return 1;
                }
            }
            else {
                std::cerr << "❌ Error: Missing value for option " << arg << std::endl;
                return 1;
            }
        }
        else {
            std::cerr << "❌ Error: Unknown option " << arg << std::endl;
            print_usage(argv[0]);
            return 1;
        }
    }
    
    std::cout << "==================================================" << std::endl;
    std::cout << "🔢 C++ Prime Number Benchmark" << std::endl;
    std::cout << "==================================================" << std::endl;
    
    PrimeBenchmark benchmark(duration);
    
    try {
        // Run benchmark with selected time
        benchmark.run_benchmark();
        
        // Generate HTML report
        benchmark.generate_html_report();
        
        std::cout << "==================================================" << std::endl;
        std::cout << "✅ Program completed successfully!" << std::endl;
        std::cout << "📊 Open benchmark_results.html in your browser" << std::endl;
        std::cout << "==================================================" << std::endl;
        
    } catch (const std::exception& e) {
        std::cerr << "❌ Error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}