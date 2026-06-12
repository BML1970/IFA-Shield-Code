#ifndef NFD_DAEMON_FW_IFASHIELD_FEATURE_HOOK_HPP
#define NFD_DAEMON_FW_IFASHIELD_FEATURE_HOOK_HPP

#include "core/common.hpp"
#include <ndn-cxx/name.hpp>
#include <unordered_map>
#include <vector>
#include <cmath>

namespace nfd {
namespace ifashield {

struct PrefixMetrics {
    time::steady_clock::TimePoint lastArrivalTime;
    std::vector<double> interArrivalTimes;
    size_t shortTermWindowCount;
    double emaRate;
    
    PrefixMetrics() 
        : shortTermWindowCount(0)
        , emaRate(0.0) {}
};

class FeatureGatheringHook {
public:
    static FeatureGatheringHook& getInstance();

    // Invoked natively inside NFD's onIncomingInterest pipeline
    void recordIncomingInterest(const Name& interestName);

    // Iterated asynchronously by the Python local_pipeline daemon via Unix socket or IPC
    std::string serializeFeaturesAndReset();

private:
    FeatureGatheringHook();
    ~FeatureGatheringHook() = default;

    std::unordered_map<std::string, PrefixMetrics> m_metricsTable;
    time::steady_clock::TimePoint m_lastWindowReset;
    
    const size_t MAX_IAT_SAMPLES = 50;
    const double ALPHA_EMA = 0.2;
    const time::milliseconds WINDOW_DURATION = time::milliseconds(1000); // 1-second sampling window
};

} // namespace ifashield
} // namespace nfd

#endif // NFD_DAEMON_FW_IFASHIELD_FEATURE_HOOK_HPP