from boutiques.descriptor2func import function
from argparse import ArgumentParser

def main(args=None):
	parser = ArgumentParser("mrtrixPpline.py")
	parser.add_argument("diffusion_image")
	parser.add_argument("bvecs",
                        help="The b-vectors corresponding to the diffusion "
                             "images. If the images have been preprocessed "
                             "then the rotated b-vectors should be used.")
	parser.add_argument("bvals",
                        help="The b-values corresponding to the diffusion "
                             "images. ")
	parser.add_argument("nodes")
	parser.add_argument("output_directory",
                        help="The directory in which the streamlines and "
                             "optionally graphs and figures will be saved in.")
	parser.add_argument("--whitematter_mask", "-wm")
	parser.add_argument("--response", "-r")
	parser.add_argument("--output_start", "-o",
			help="Affects how the output files called. (e.g. '-o sub-A0000' will give output files sub-A0000_output_mask.nii.gz")

	results = parser.parse_args() if args is None else parser.parse_args(args)

	if results is None:
		return 0

	if results.output_start is None:
		results.output_start = "mrtrixPpline"

	results.output_styling = results.output_directory+results.output_start

	if results.whitematter_mask is None:
		dwi2mask = function("dwi2mask_desc.json")
		mask_out = dwi2mask(input=results.diffusion_image, 
							bvals=results.bvals,
							bvecs=results.bvecs,
							fslgrad=True,
							output_mask=results.output_styling+"_output_mask.nii.gz")
		print(mask_out)
		results.whitematter_mask = results.output_styling+"_output_mask.nii.gz"

	if results.response is None:
		dwi2response = function("dwi2response_tournier_desc.json")
		response_out = dwi2response(input=results.diffusion_image, 
									bvals=results.bvals,
									bvecs=results.bvecs,
									fslgrad=True,
									output=results.output_styling+"_output_response.txt")
		print(response_out)
		results.response = results.output_styling+"_output_response.txt"

	dwi2fod = function("dwi2fod_desc.json")
	fod_out = dwi2fod(algorithm="csd",
						dwi=results.diffusion_image, 
						bvals=results.bvals,
						bvecs=results.bvecs,
						fslgrad=True,
						odf=results.output_styling+"_output_fod.nii.gz",
						mask=results.whitematter_mask,
    response=results.response)
	print(fod_out)

	tckgen = function("tckgen_desc.json")
	tck_out = tckgen(seed_image=results.diffusion_image, 
						bvals=results.bvals,
						bvecs=results.bvecs,
						fslgrad=True,
						source=results.output_styling+"_output_fod.nii.gz",
						tracks=results.output_styling+"_output_tracks.tck",
						mask_bin_mask=results.whitematter_mask)
	print(tck_out)

	connectomegen = function("tck2connectome_desc.json")
	connectome_out = connectomegen(input_nodes=results.nodes,
									input_tracks=results.output_styling+"_output_tracks.tck",
									output_connectome=results.output_styling+"_output_connectome.csv")
	print(connectome_out)

main()
