#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(){
	for(int i = 10;i<=20;i++){
		int length = 1 << i;		
		char name[1024];
		itoa(length,name,10);
		strcat(name,".txt");
		printf("%s\n",name);
	}
	return 0;
}

