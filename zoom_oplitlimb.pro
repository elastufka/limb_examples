function get_center, flare_list,i ;does this require wcs coords conversion? probably...
    locstr=flare_list.flare_properties.location[i]
    xy=strsplit(locstr,';',/extract) ; why can't these be iterables?!!!!
    center=[fix(strmid(xy[0],4,strlen(xy[0])-2)),fix(strmid(xy[1],0,strlen(xy[1])-4))]
    return, center
    end

function convert_coords,header_aia, header_euv,center
    wcs_aia=fitshead2wcs(header_aia) 
    coord=wcs_get_coord(wcs_aia,center) ;helioprojective @ AIA position->wcs
    wcs_euv=fitshead2wcs(header_euv)
    lon=coord[1]
    lat=coord[0]
    ;wcs_convert_from_coord,wcs_aia,coord,'hg',lon,lat ;helioprojective @AIA->Stonyhurst heliographic
    wcs_convert_to_coord,wcs_euv,newcoord2,'hg',lon,lat
    pix=wcs_get_pixel(wcs_euv,newcoord2)
    print, center,coord,newcoord2,pix
    wcs_euv=fitshead2wcs(header_euv)
    test= wcs_get_coord(wcs_euv,[-300,-300]) 
    ;print, test,wcs_get_pixel(wcs_euv,test)
    xyidl=wcs_get_pixel(wcs_euv,coord) ;wcs -> pixel on STEREO image ... I think I need to go through stonyhurst first
    return, xyidl
    end

;function find_center, wcs_aia,wcs_euv,center ;consider instead getting the limb coords first and the just using the latitude lines to guess? if coord conversion proves too difficult
  
    
function format_datetime,flare_list,i,aia=aia,euv=euv,prepped=prepped ;cuz IDL sucks at datetimes
    dt=flare_list.Datetimes.Messenger_datetimes[i]      ;this is a string
    print,dt
    if keyword_set(aia) then ffname='aia_lev1_*'+strmid(dt,0,4)+'_'+strmid(dt,5,2)+'_'+strmid(dt,8,2)+'*.fits'
    if keyword_set(euv) then ffname=strmid(dt,0,4)+strmid(dt,5,2)+strmid(dt,8,2)+'_*eub.*fts'
    if keyword_set(prepped) then ffname='AIA'+strmid(dt,0,4)+strmid(dt,5,2)+strmid(dt,8,2)+'*304.fits'
    return, ffname
    end

pro zoom_oplotlimb, flare_list, ivec=ivec, quiet=quiet,fov=fov
    loadct,9
    llen = size(flare_list.ID,/dim)
    if ~keyword_set(ivec) then ivec=findgen(llen[0])
    if ~keyword_set(fov) then fov=[10,10]
    for i=0,1 do begin ;llen[0]-1 do begin
        ;flare=flare_list(ivec[i]) doesn't work
        i=1
        center=get_center(flare_list,i)
       
        ffname = format_datetime(flare_list,i,/aia)
        fitsfile=file_search('/Users/wheatley/sunpy/data/'+ffname)
                                ;if fitsfile ne '' then
        read_sdo,fitsfile[0],hdr,data
        aia_prep,hdr,data,header_aia,data_aia 
        ;aia_prep,fitsfile,[1],/do_write_fits,outdir='/Users/wheatley/sunpy/data/'
        ;header_aia=headfits(header_aia)
        
        ffname = format_datetime(flare_list,i,/euv)
        fitsfile=file_search('/Users/wheatley/sunpy/data/'+ffname)
        print, fitsfile[0]
        ;if fitsfile ne '' then
        header_euv=headfits(fitsfile[0])

        wcs_aia=convert_coords(header_aia,header_euv,center)
        ;print, center,wcs_aia
        fits2map,fitsfile[0],map_euv        
        oue
        plot_map,map_euv,fov=fov,center=wcs_aia,/log
        map_oplot_limb_from_earth, map_euv,color=255,linestyle=2,roll_angle_range=[90,270]
        filename='data/stereo-aia/'+ strtrim(string(flare_list.id[i]),1) +'EUVIlimb.png'
        write_png, filename, tvrd(/true)
    endfor
end


