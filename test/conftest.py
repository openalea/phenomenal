import os

# plt.show() must not open windows waiting to be closed. This has to be set
# before matplotlib is imported, so it comes before the import of test modules.
os.environ["MPLBACKEND"] = "Agg"
