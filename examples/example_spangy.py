
import slam.io as sio
import numpy as np
import slam.differential_geometry as sdg
import slam.curvature as scurv
from scipy.sparse.linalg import eigsh
import time
import slam.plot as splt
import matplotlib.pyplot as plt
import slam.spangy as spgy

# MESH IS STORED IN THE SPANGY FOLDER
mesh = sio.load_mesh('../spangy/Data/mar0003_recons_nobias_cortex_smooth_hemil.bouchee.gii')
N = 1500
#Call the eigenvector and value function
eigVal, eigVects, lap_b = spgy.spangy_eigenpairs(mesh,N)

#load the eigenvectors and eigenvalues generated by Python
# eigVects = np.loadtxt("../spangy/Data/mar0003_recons_nobias_cortex_smooth_hemil.bouchee.eigVects_py.txt")
# eigVal = np.loadtxt("../spangy/Data/mar0003_recons_nobias_cortex_smooth_hemil.bouchee.eigVal_py.txt")

#Load the eigenvectors and values generated by MATLAB
# eigVal_mat = np.loadtxt("../spangy/Data/mar0003_recons_nobias_cortex_smooth_hemil.bouchee_eigenvalues_1500.txt", delimiter=",")
# eigVects_mat = np.loadtxt("../spangy/Data/mar0003_recons_nobias_cortex_smooth_hemil.bouchee_eigenvectors_1500.txt", delimiter=",")

#reverse order of eigVal_mat
# eigVal_mat = eigVal_mat[::-1]

#Test that the values are the same, with a tolerance of 1e-6
# assert np.allclose(eigVal,eigVal_mat,rtol=1e-6,atol=1e-6) #True
#Test that the vectors are the same, with a tolerance of 1e-6
# assert np.allclose(np.abs(eigVects),np.abs(eigVects_mat),rtol=1e-6,atol=1e-6)  #True

## CURVATURE
PrincipalCurvatures, PrincipalDir1, PrincipalDir2 = \
    scurv.curvatures_and_derivatives(mesh)

gaussian_curv = PrincipalCurvatures[0, :] * PrincipalCurvatures[1, :]

mean_curv = 0.5 * (PrincipalCurvatures[0, :] + PrincipalCurvatures[1, :])

#save mean curv to disk as txt
np.savetxt("../spangy/Data/mar0003_recons_nobias_cortex_smooth_hemil.bouchee.mean_curv_python.txt",mean_curv)

# load curvature from matrix
#gaussian_curv = np.loadtxt("../Data/mar0003_recons_nobias_cortex_smooth_hemil.bouchee_curv_1500.txt", delimiter=",")
#mean_curv = -gaussian_curv

####### SPECTRUM
grouped_spectrum,group_indices,coefficients = spgy.spangy_spectrum(mean_curv, lap_b, eigVects, eigVal)
levels=len(group_indices)

### SPECTRAL BANDS
loc_dom_band, frecomposed = spgy.spangy_local_dominance_map(coefficients,mean_curv,levels,group_indices,eigVects)

#save loc_dom_band and frecomposed to disk as txt
np.savetxt("../spangy/Data/mar0003_recons_nobias_cortex_smooth_hemil.bouchee.loc_dom_band_python.txt",loc_dom_band)
np.savetxt("../spangy/Data/mar0003_recons_nobias_cortex_smooth_hemil.bouchee.frecomposed_python.txt",frecomposed)

## Convert previous MATLAB code to Python
# a. Whole brain parameters
mL_in_MM3=1000
CM2_in_MM2=100
volume = mesh.volume
surface_area = mesh.area
afp=np.sum(grouped_spectrum[1:])
print('** a. Whole brain parameters **')
print('Volume = %d mL, Area = %d cm^2, Analyze Folding Power = %f,' % (np.floor(volume/mL_in_MM3),np.floor(surface_area/CM2_in_MM2),afp))

# b. Band number of parcels
print('** b. Band number of parcels **')
print('B4 = %f, B5 = %f, B6 = %f' % (0,0,0))

# c. Band power
print('** c. Band power **')
print('B4 = %f, B5 = %f, B6 = %f' % (grouped_spectrum[4],grouped_spectrum[5],grouped_spectrum[6]))

# d. Band relative power
print('** d. Band relative power **')
print('B4 = %0.5f, B5 = %0.5f , B6 = %0.5f' % (grouped_spectrum[4]/afp,grouped_spectrum[5]/afp,grouped_spectrum[6]/afp))

#Create two subplots
fig, (ax1, ax2) = plt.subplots(1, 2)
# Plot the sqrt of the eigVals divided by 2*np.pi against the coefficients in the first subplot
#plot with line
ax1.plot(np.sqrt(eigVal[1:])/(2*np.pi),coefficients[1:])
#add the labels and title
ax1.set_xlabel('Frequency (m^{-1})')
ax1.set_ylabel('coefficients')

#Barplot for the nlevels and grouped spectrum in the second subplot
# Barplot in ax2 between nlevels and grouped spectrum
print(grouped_spectrum)
ax2.bar(np.arange(0,levels),grouped_spectrum.squeeze())
#add the labels and title
ax2.set_xlabel('Spangy frequency bands')
ax2.set_ylabel('Power spectrum')

plt.show()
