// Add this include at the top of daemon/fw/forwarder.cpp
#include "fw/ifashield-feature-hook.hpp"

// Locate the following function implementation inside forwarder.cpp
void
Forwarder::onIncomingInterest(const FaceEndpoint& ingress, const Interest& interest)
{
  // -------------------------------------------------------------
  // FL-IFAshield NATIVE REGISTER ENTRY POINT HOOK
  // -------------------------------------------------------------
  nfd::ifashield::FeatureGatheringHook::getInstance().recordIncomingInterest(interest.getName());
  // -------------------------------------------------------------

  // Original native NFD pipeline logic continues below...
  NFD_LOG_DEBUG("onIncomingInterest face=" << ingress.face.getId() << " interest=" << interest.getName());
  
  if (interest.getName().size() > Name::MAX_DEPTH) {
    NFD_LOG_DEBUG("onIncomingInterest interest=" << interest.getName() << " depth exceeds limit");
    return;
  }
  
  // ... Rest of original NFD forwarding processing code
}