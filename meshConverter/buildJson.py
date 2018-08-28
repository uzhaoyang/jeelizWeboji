#!/usr/bin/python 
import os
import os.path
import sys
import json
import pdb


# SETTINGS
TMPPATH='./tmp/'
OUTPUTPATH='../assets/3D/meshes/'

# get command line arguments
if len(sys.argv)==1:
	print 'Invalid usage. usage : buildMorphs.py <morphPath>'
	exit(0)
morphPath=sys.argv[1]
INPUTPATH ='./meshes/'+morphPath+'/'
OUTPUTNAME=morphPath+'.json'

# begin funcz
def exec_cmd(cmd):
	print('EXEC :'+cmd)
	os.system(cmd)

def parse_facegenOBJ(objURL, label): # read a wavefront obj file generated by facegen
	with open(objURL, 'r') as file_handler:
		objContent = file_handler.read()
		objContentLines=objContent.split("\n")
		vertices=[]
		vts=[]
		faces=[]
		for line in objContentLines:
			line=line.replace('\t', ' ')
			line=line.replace('  ', ' ')
			lineSplitted=line.split(' ')
			print('line = %s' % line)
			cmd=lineSplitted.pop(0)
			if cmd=='v':
				x=float(lineSplitted.pop(0))
				y=float(lineSplitted.pop(0))
				z=float(lineSplitted.pop(0))
				vertices.append([x,y,z])
			elif cmd=='vt':
				u=float(lineSplitted.pop(0))
				v=float(lineSplitted.pop(0))
				vts.append([u,v])
			elif cmd=='f':
				fa=lineSplitted.pop(0).split('/')
				fb=lineSplitted.pop(0).split('/')
				fc=lineSplitted.pop(0).split('/')
				if len(lineSplitted)>0:
				    fd=lineSplitted.pop(0).split('/')
				else:
					fd=[]
				#face=[[int(fa[0])-1, int(fa.pop())-1], [int(fb[0])-1, int(fb.pop())-1], [int(fc[0])-1, int(fc.pop())-1]]
				face=[[int(fa[0])-1, int(fa[1])-1], [int(fb[0])-1, int(fb[1])-1], [int(fc[0])-1, int(fc[1])-1]]
				if len(fd)>1: #quad face, otherwise tri face
					face.append([int(fd[0])-1, int(fd[1])-1])
				faces.append(face)
		return {'vertices':vertices,'vts':vts,'faces':faces}

def compact_vecList(myList, precision): # round a float list
	for vec in myList:
		for i in range(0, len(vec)):
			vec[i]=round(vec[i], precision)
			if vec[i]==0.0:
				vec[i]=0


# end funcz
outputMorphJSON=OUTPUTPATH+OUTPUTNAME
print('INFO in buildMorph.py : INPUTPATH = %s , outputMorphJSON = %s' % (INPUTPATH, outputMorphJSON) )


 # clean all
exec_cmd('rm -f '+outputMorphJSON)
exec_cmd('rm -f '+TMPPATH+'*')


# read base morphs
outputJSON={'base': False, 'morphs': []}
base=parse_facegenOBJ(INPUTPATH+'base.obj', 'BASE')
compact_vecList(base['vertices'], 4)
compact_vecList(base['vts'], 4)
outputJSON['base']=base

# add all morphs
i=0
while True:
	morphURL1 = INPUTPATH+'morph'+str(i)+'.obj'
	morphURL2 = INPUTPATH+'morph'+'_'+str(i)+'.obj'
	if os.path.isfile(morphURL1):
		morphURL = morphURL1
	elif os.path.isfile(morphURL2):
		morphURL = morphURL2
	else:
		print('Stop after %d morphs' % i)
		break
	morph=parse_facegenOBJ(morphURL, 'MORPH'+str(i))
	dVertices=morph['vertices']
	nMorphsVertices=min(len(base['vertices']), len(dVertices))
	if len(base['vertices'])!=len(dVertices):
		print('WARNING for morph %s : it has %d vertices but the base mesh has %d vertices' %(objURL, len(dVertices), len(base['vertices'])))
	for j in range(0, nMorphsVertices):
		dVertices[j][0]-=base['vertices'][j][0] #x
		dVertices[j][1]-=base['vertices'][j][1] #y
		dVertices[j][2]-=base['vertices'][j][2] #z
	compact_vecList(dVertices, 4)
	outputJSON['morphs'].append(dVertices)
	i+=1

# dump output to the file
print('INFO : write output into file %s' % outputMorphJSON)
with open(outputMorphJSON, 'w') as f:
     json.dump(outputJSON, f, separators=(',',':'))

print('/DONE bro')
