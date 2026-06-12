#include "ifashield-feature-hook.hpp"
#include "core/logger.hpp"

NFD_LOG_INIT(IFAshieldHook);

namespace nfd {
namespace ifashield {

FeatureGatheringHook& FeatureGatheringHook::getInstance() {
    static FeatureGatheringHook instance;
    return instance;
}

FeatureGatheringHook::FeatureGatheringHook() {
    m_lastWindowReset = time::steady_clock::now();
}

void FeatureGatheringHook::recordIncomingInterest(const Name& interestName) {
    auto now = time::steady_clock::now();
    
    // Aggregate data at a higher hierarchical level (e.g., first 3 components) to catch broad floods
    std::string trackedPrefix = interestName.getPrefix(std::min(interestName.size(), size_t(3))).toUri();
    
    auto& metrics = m_metricsTable[trackedPrefix];
    
    // 1. Calculate Inter-Arrival Time (IAT) metrics for temporal burstiness (sigma_iat)
    if (metrics.lastArrivalTime != time::steady_clock::TimePoint()) {
        auto iat = time::duration_cast<time::microseconds>(now - metrics.lastArrivalTime).count() / 1000000.0;
        metrics.interArrivalTimes.push_back(iat);
        
        if (metrics.interArrivalTimes.size() > MAX_IAT_SAMPLES) {
            metrics.interArrivalTimes.erase(metrics.interArrivalTimes.begin());
        }
    }
    metrics.lastArrivalTime = now;

    // 2. Track raw surges in current window (B_req)
    metrics.shortTermWindowCount++;

    // Continuous evaluation of the sliding telemetry time-barrier
    if (now - m_lastWindowReset >= WINDOW_DURATION) {
        for (auto& pair : m_metricsTable) {
            auto& m = pair.second;
            // 3. Update the Exponential Moving Average for tracking long-term trends (EMA_rate)
            m.emaRate = (ALPHA_EMA * m.shortTermWindowCount) + ((1.0 - ALPHA_EMA) * m.emaRate);
        }
        // Defer counter resets to serialization cycle to maintain snapshot consistency
    }
}

std::string FeatureGatheringHook::serializeFeaturesAndReset() {
    auto now = time::steady_clock::now();
    std::stringstream ss;
    
    // CSV Schema Format: Prefix, Sigma_IAT, B_req, EMA_rate
    for (auto& pair : m_metricsTable) {
        const std::string& prefix = pair.first;
        auto& m = pair.second;
        
        // Compute standard deviation of Inter-Arrival Times (sigma_iat)
        double sigma_iat = 0.0;
        if (m.interArrivalTimes.size() > 1) {
            double sum = 0.0;
            for (double val : m.interArrivalTimes) sum += val;
            double mean = sum / m.interArrivalTimes.size();
            
            double sq_sum = 0.0;
            for (double val : m.interArrivalTimes) sq_sum += (val - mean) * (val - mean);
            sigma_iat = std::sqrt(sq_sum / (m.interArrivalTimes.size() - 1));
        }
        
        ss << prefix << "," 
           << sigma_iat << "," 
           << m.shortTermWindowCount << "," 
           << m.emaRate << "\n";
           
        // Reset short term window burst counters post-extraction
        m.shortTermWindowCount = 0;
    }
    
    m_lastWindowReset = now;
    return ss.str();
}

} // namespace ifashield
} // namespace nfd