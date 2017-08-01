# This program should run in the file folder that contains the file folder "cut_co".  Or you can change the path to the directory you want under in the "data_name" .
# There should be three folders inside "cut_co", "xycut_co" that contains all the fits file, "movies" where all the movies will be saved to, and "colormaps" where all the colormaps will be saved to.

from math import radians
import yt
import numpy as np
from IPython.core.display import Image
from yt.visualization.volume_rendering.transfer_function_helper import TransferFunctionHelper
from yt.visualization.volume_rendering.render_source import VolumeSource
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as mpatches
from astropy.io import fits
from astropy.stats import mad_std
from yt.units import K
from subprocess import call

# Or you can put all the file names in here in the list to run it all at one time. Might take really long though...
list=['UGC04132.co.xycut.K.fits']

rotate_angle_per_time=5 # in degrees

frames_per_sec="5" # for making the video using ffmpeg


def makemovie(name):
    data_name='cut_co/xycut_co/'+name

    ds=yt.load(data_name,nan_mask = 0.0)



    sc = yt.create_scene(ds,"intensity")
    source = sc[0]
    sc.annotate_domain(ds,color=[128/255,128/255,128/255,0.01])
    sc.annotate_axes(alpha=0.1)
    source.set_log(False)
    source.tfh.build_transfer_function()
    sc.camera.switch_orientation(normal_vector=[-0.1,-0.1,-9])
    sc.camera.set_resolution((1024,1024))
    sc.camera.roll(radians(-180))


    header=fits.getheader(data_name)
    data=fits.getdata(data_name)
    obj1=header['object']
    obj=obj1.strip()

    max1=ds.r['intensity'].max()

    max=max1/K

    sig=mad_std(data, ignore_nan=True) # Older astropy version does not support ignore_nan argument. Delete it and the code will run.


    tf2 = yt.ColorTransferFunction((sig, max))

    tf2.add_gaussian(3*sig, sig/100, [106/255, 90/255, 205/255, 0.6])

    tf2.add_gaussian(5*sig, sig/100, [30/255, 144/255, 1, 1.0])

    if max>18*sig:
        tf2.add_gaussian(0.4*max, sig/100, [0, 1, 127/255, 1.4])
    
        tf2.add_gaussian(0.54*max, sig/100, [1, 215/255, 0, 1.8])
    
        tf2.add_gaussian(0.68*max, sig/100, [1, 0, 0, 2.8])
    
        tf2.add_gaussian(0.85*max, sig/100, [240/255, 1, 1, 3.8])

    else:
    
        tf2.add_gaussian(7*sig, sig/100, [0, 1, 127/255, 1.4])

        tf2.add_gaussian(9*sig, sig/100, [1, 215/255, 0, 1.8])
    
        tf2.add_gaussian(11.5*sig, sig/100, [1, 0, 0, 2.8])
    
        tf2.add_gaussian(13.5*sig, sig/100, [240/255, 1, 1, 3.8])



    command3='mkdir cut_co/'+obj
    command4='mkdir cut_co/'+obj+'/movie'
    call(command3, shell=True)
    call(command4, shell=True)




    save_place='cut_co/'+obj+'/movie'

    source.set_transfer_function(tf2)
    source.tfh.tf=tf2

#-----------------------------makeing the colormap------------------------------------------------
    if max>18*sig:
        white_patch = mpatches.Patch(color='#F0FFFF', label='0.85 max')
        red_patch = mpatches.Patch(color='#FF0000', label='0.68 max')
        yellow_patch = mpatches.Patch(color='#FFD700', label='0.54 max')
        green_patch = mpatches.Patch(color='#00FF7F', label='0.4 max')
        blue_patch = mpatches.Patch(color='#1E90FF', label='5 $\sigma$')
        purple_patch = mpatches.Patch(color='#6A5ACD', label='3 $\sigma$')
    else:
        white_patch = mpatches.Patch(color='#F0FFFF', label='13.5 $\sigma$')
        red_patch = mpatches.Patch(color='#FF0000', label='11.5 $\sigma$')
        yellow_patch = mpatches.Patch(color='#FFD700', label='9 $\sigma$')
        green_patch = mpatches.Patch(color='#00FF7F', label='7 $\sigma$')
        blue_patch = mpatches.Patch(color='#1E90FF', label='5 $\sigma$')
        purple_patch = mpatches.Patch(color='#6A5ACD', label='3 $\sigma$')

    source.tfh.plot(save_place+'/transfer_function.png')

    img=mpimg.imread(save_place+'/transfer_function.png')
    fig, ax = plt.subplots(figsize=(8,4))

    imgnew=np.delete(img,np.arange(0,77),1)

    imgplot = plt.imshow(imgnew)

    ax.axis('off')

    plt.legend(handles=[white_patch, red_patch,yellow_patch,green_patch,blue_patch,purple_patch],loc=(0.91,0.4),prop={'size':9})
                                  
    plt.savefig('cut_co/colormaps/colormap_'+obj+'.png', bbox_inches='tight')

#----------------------------------------------------------------------------------------------------


    i=0
    j=1
    while i<180:
        sc.camera.yaw(radians(rotate_angle_per_time)) #rotate about the north vector
        sc.save(save_place+'/pic'+str(j)+'.png',sigma_clip=4.5)
        i+=rotate_angle_per_time
        j+=1
    


#I zoomed in 1.07 times for 9 times/frames
    k=0
    l=j
    while k<=8:
        sc.camera.zoom(1.07)
        sc.camera.yaw(radians(rotate_angle_per_time))
        sc.save(save_place+'/pic'+str(l)+'.png', sigma_clip=4.5)
        k+=1
        l+=1


    a=l
    b=0
    while b<360:
        sc.camera.yaw(radians(rotate_angle_per_time))
        sc.save(save_place+'/pic'+str(a)+'.png',sigma_clip=4.5)
        b+=rotate_angle_per_time
        a+=1

    num_of_frames=str(a)





    command="ffmpeg -r "+frames_per_sec+" -f image2 -s 1920x1080 -start_number 1 -i "+save_place+"/pic%d.png -vframes "+num_of_frames+" -vcodec libx264 -crf 15  -b 5000K -vb 20M -pix_fmt yuv420p "+save_place+"/movie.mp4"

    command2="ffmpeg -i "+save_place+"/movie.mp4 -vf drawtext=\"fontfile=/Library/Fonts/SignPainter.ttc: \\"+obj+": fontcolor=white: fontsize=33: x=(w-text_w)/8: y=(h-text_h)/8\" -codec:a copy cut_co/movies/"+obj+".mp4"

    call(command, shell=True)

    call(command2, shell=True)





for i in list:
    makemovie(i)




