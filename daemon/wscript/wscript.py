# Inside daemon/wscript under the file scanning definition blocks
fw_sources = bld.path.ant_glob([
    'fw/*.cpp',
    # Ensure our extension hook module compiles inside the daemon namespace
    'fw/ifashield-feature-hook.cpp'
])