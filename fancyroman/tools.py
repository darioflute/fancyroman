def select_gaia(ra, dec, radius=1.0, star=0.7, maglim=16.5):
    """
    Inputs
    ------
    ra (float): Right ascension of the field center
    dec (float): Declination of the field center
    radius (float): Search radius in degrees
    star (float): Threshold to select starlike sources
    maglim (float): Limit in brightness of the accepted sources

    Output
    ------
    List of GAIA sources in Skycoord

    Description
    -----------
    To use this function, select at least ra,dec of the intended field:

        >>> gaia_catalog = select_gaia(ra=30, dec=-45, radius=1.0)
    
    The function will return a catalog of GAIA stars in the Roman I-Sim format.
    Any sources without fluxes or positions is filtered out.
    """
    from astroquery.gaia import Gaia
    from astropy.coordinates import SkyCoord
    import numpy as np

    query = f'SELECT * FROM gaiadr3.gaia_source WHERE distance({ra}, {dec}, ra, dec) < {radius}'
    job = Gaia.launch_job_async(query)
    result = job.get_results()

    result = result[result['classprob_dsc_combmod_star'] >= star]
    result = result[result['phot_g_mean_mag'] < maglim]

    stars = SkyCoord(result['ra'].value.data, result['dec'].value.data, unit='deg', frame = 'icrs')
    return stars


def unsaturate_psf(L2, stars, output=None):
    """
    The code applies the correct PSF to the list of stars in the Roman L2 image.

    Inputs
    ------
    L2 - name of the L2 file
    stars:  list of stars (or point-like objects) which have saturated of highly non-linear PSF center
            the list is in Skycoords from astropy (frame='icrs')
    output: optional name of output file with corrected PSF. If not given the output name is the same as the input name with a "_us" at the end of the name.
    """
    import roman_datamodels as rdm
    import h5py
    import numpy as np
    import os

    # Input L2 file
    with rdm.open(L2) as dm:
        image = dm.data.copy()
        wfidetector = dm.meta.instrument.detector
        wfioptelement = dm.meta.instrument.optical_element
        wcs = dm.meta.wcs

    # Select the correct PSF
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"data") # data directory in the distribution
    with h5py.File(os.path.join(path, 'epsf_'+wfioptelement+'.h5'), 'r') as hdf5_file:
        psf = hdf5_file[wfidetector][:]

    # Centers of the empirical PSFs
    xpsf = np.array([4.0, 2047.5, 4091.0, 4.0, 2047.5, 4091.0, 4.0, 2047.5, 4091.0])
    ypsf = np.array([4.0, 4.0, 4.0, 2047.5, 2047.5, 2047.5, 4091.0, 4091.0, 4091.0])

    # Regions and meshgrid to compute background and normalization
    r_int, r_ext, r_bkg_int , r_bkg_ext = 3.5,5,12,17
    xv, yv = np.meshgrid(np.arange(35)-17, np.arange(35)-17, indexing='ij')
    distance = np.hypot(xv,yv)

    # Trasform the list of stars in x, y coordinates and select stars inside image
    ra, dec = stars.ra.deg, stars.dec.deg
    x, y = wcs.backward_transform(ra, dec)
    idx = (x >= 17) & (x < 4088-17) & (y >= 17) & (y < 4088-17)    
    x, y = x[idx], y[idx]

    # Central pixel of subimage and distance of star from central pixel in 1/10 of pixel
    xx = np.round(x - 0.5).astype(int)
    yy = np.round(y - 0.5).astype(int)
    dx = np.round((x - np.floor(x) - 0.5)*10).astype(int)
    dy = np.round((y - np.floor(y) - 0.5)*10).astype(int)

    for i in range(len(x)):
        # Selection of PSF positions
        dpsf = np.hypot(x[i]-xpsf, y[i]-ypsf)
        idpsf = np.argmin(dpsf)
        data = psf[1,idpsf]
        # Compute the PSF down to L2 images' resolution
        br = block_reduce(data[5+dy[i]:-6+dy[i],5+dx[i]:-6+dx[i]], 10, func=np.sum)
        # Selection of subimage
        subimage = image[yy[i]-17:yy[i]+18, xx[i]-17:xx[i]+18]

        # Computation of normalization and substitution
        idx_int = distance <= r_int
        idx_ext = (distance >= r_int) & (distance < r_ext)
        idx_bkg = (distance >= r_bkg_int) & (distance < r_bkg_ext)        
        psfext = np.median(br[idx_ext])
        psfbkg = np.median(br[idx_bkg])
        srcext = np.median(subimage[idx_ext])
        srcbkg = np.median(subimage[idx_bkg])
        normalization = (srcext - srcbkg)/(psfext - psfbkg)
        subimage[idx_int] = br[idx_int] * normalization
        image[yy[i]-17:yy[i]+18, xx[i]-17:xx[i]+18] = subimage

    # Save the corrected image
    if output is None:
        infile = os.path.abspath(L2)
        path, filename = os.path.split(infile)
        filename, ext = os.path.splitext(os.path.split(infile)[1])
        output = os.path.join(path, filename+'_us'+ext)    
    with rdm.open(L2) as dm:
        dm.data = image
        dm.save(output)
